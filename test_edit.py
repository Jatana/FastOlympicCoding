import sublime, sublime_plugin
import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
import shlex
from sublime import Region, Phantom, PhantomSet
from os import path
from importlib import import_module
from time import time
import threading

from .Modules.ProcessManager import ProcessManager
from .settings import base_name, get_settings, root_dir
from .debuggers import debugger_info
from .Highlight.CppVarHighlight import highlight
from .Highlight.test_interface import get_test_styles


class TestEditCommand(sublime_plugin.TextCommand):
	BEGIN_TEST_STRING = 'Test %d {'
	OUT_TEST_STRING = ''
	END_TEST_STRING = '} rtcode %s'
	REGION_BEGIN_KEY = 'test_begin_%d'
	REGION_OUT_KEY = 'test_out_%d'
	REGION_END_KEY = 'test_end_%d'
	REGION_POS_PROP = ['', '', sublime.HIDDEN]
	REGION_ACCEPT_PROP = ['string', 'dot', sublime.HIDDEN]
	REGION_DECLINE_PROP = ['variable.c++', 'dot', sublime.HIDDEN]
	REGION_UNKNOWN_PROP = ['text.plain', 'dot', sublime.HIDDEN]
	REGION_OUT_PROP = ['entity.name.function.opd', 'bookmark', sublime.HIDDEN]
	REGION_BEGIN_PROP = ['string', 'Packages/FastOlympicCoding/icons/arrow_right.png', \
				sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE | \
					sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY_AS_OVERWRITE]
	REGION_END_PROP = ['variable.c++', 'Packages/FastOlympicCoding/icons/arrow_left.png', sublime.HIDDEN]
	REGION_LINE_PROP = ['string', 'dot', \
				sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE | \
					sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY_AS_OVERWRITE]

	# Test
	# REGION_POS_PROP = REGION_UNKNOWN_PROP

	def __init__(self, view):
		self.view = view
		self.use_debugger = False
		self.delta_input = 0
		self.tester = None
		self.session = None
		self.phantoms = PhantomSet(view, 'test-phantoms') 

	def insert_text(self, edit, text=None):
		v = self.view
		if text is None:
			if not self.tester.proc_run:
				return None
			to_shove = v.substr(Region(self.delta_input, v.sel()[0].b))
			# print('shovel -> ', to_shove)
			v.insert(edit, v.sel()[0].b, '\n')

		else:
			to_shove = text
			v.insert(edit, v.sel()[0].b, to_shove + '\n')
		self.delta_input = v.sel()[0].b 
		self.tester.insert(to_shove + '\n')

	def insert_cb(self, edit):
		v = self.view
		s = sublime.get_clipboard()
		lst = s.split('\n')
		for i in range(len(lst) - 1):
			self.tester.insert(lst[i] + '\n', call_on_insert=True)
		self.tester.insert(lst[-1], call_on_insert=True)

	def open_test_edit(self, i):
		v = self.view
		edit_view = v.window().new_file()
		v.window().set_view_index(edit_view, 1, 1)

	def on_test_action(self, i, event):
		v = self.view
		tester = self.tester
		if event == 'test-click':	
			self.toggle_fold(i)	
		elif event == 'test-edit':
			self.open_test_edit(i)

	def on_accdec_action(self, i, event):
		v = self.view
		tester = self.tester
		if event == 'click-acc':
			tester.accept_out(i)
		elif event == 'click-dec':
			tester.decline_out(i)
		self.update_configs()
		self.memorize_tests()

	def cb_action(self, event):
		v = self.view
		if event == 'test-save':	
			for sub in v.window().views():
				if sub.id() == self.source_view_id:
					sub.run_command('test_manager', {
						'action': 'set_test_input',
						'data': v.substr(Region(1, v.size())),
						'id': self.test_id
					})
					v.close()
					break	

		elif event == 'test-delete':
			for sub in v.window().views():
				if sub.id() == self.source_view_id:
					sub.run_command('test_manager', {
						'action': 'delete_test',
						'id': self.test_id
					})
					v.close()
					break

	def update_config(self):
		v = self.view
		styles = get_test_styles(v)
		content = open(root_dir + '/Highlight/test_edit.html').read()

		content = content.format(
			test_id=self.test_id,
		)
		content = '<style>' + styles + '</style>' + content

		phantom = Phantom(Region(0), content, sublime.LAYOUT_BLOCK, self.cb_action)

		self.phantoms.update([phantom])

	def memorize_tests(self):
		# print([x.memorize() for x in (self.tester.get_tests())])
		f = open(self.dbg_file + ':tests', 'w')
		f.write(sublime.encode_value([x.memorize() for x in (self.tester.get_tests())], True))
		f.close()

	def add_region(self, line, region_prop):
		v = self.view
		pos = v.line(line)
		from random import randint
		v.add_regions(str(randint(0, 1e9)), [Region(pos.a, pos.a + 1)], *region_prop)

	def toggle_side_bar(self):
		self.view.window().run_command('toggle_side_bar')

	def change_process_status(self, status):
		# name = self.view.name()
		# self.view.set_name(name[:name.index(' ')] + ' -' + status.lower())
		self.view.set_status('process_status', status)

	def clear_all(self):
		v = self.view
		v.run_command('test_manager', {'action': 'erase_all'})
		if self.tester:
			v.erase_regions('type')
			for i in range(-1, self.tester.test_iter + 1):
				v.erase_regions(self.REGION_BEGIN_KEY % i)
				v.erase_regions(self.REGION_END_KEY % i)
				v.erase_regions('line_%d' % i)
				v.erase_regions('test_error_%d' % i)

	def init(self, edit, run_file=None, build_sys=None, clr_tests=False, \
		test='', source_view_id=None, test_id=None, load_session=False):
		v = self.view

		self.delta_input = 0
		self.test_id = test_id
		self.source_view_id = source_view_id

		v.set_scratch(True)
		v.set_name('test ' + str(test_id) + ' -edit')
		v.run_command('toggle_setting', {'setting': 'line_numbers'})
		v.run_command('set_setting', {'setting': 'fold_buttons', 'value': False})
		v.settings().set('edit_mode', True)
		v.set_syntax_file('Packages/%s/TestSyntax.tmLanguage' % base_name)
		v.insert(edit, 0, '\n' + test)
		self.update_config()

	def get_style_test_status(self, nth):
		check = self.tester.check_test(nth)
		if check:
			return self.REGION_ACCEPT_PROP
		elif check is False:
			return self.REGION_DECLINE_PROP
		return self.REGION_UNKNOWN_PROP

	def sync_read_only(self):
		view = self.view
		if view.settings().get('edit_mode'):
			view.set_read_only(False)
			return
		have_sel_no_end = False
		for sel in view.sel():
			if sel.begin() != view.size():
				have_sel_no_end = True
				break

		end_cursor = len(view.sel()) and \
			((self.tester is None) or (not self.tester.proc_run)) and \
			view.size() == view.sel()[0].a

		# view.set_read_only(have_sel_no_end or end_cursor)

	def get_begin_region(self, id):
		v = self.view
		return v.get_regions(self.REGION_BEGIN_KEY % id)

	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False, \
			test='', source_view_id=None, var_name=None, test_id=None, pos=None, \
			load_session=False, region=None, frame_id=None):
		v = self.view
		pt = v.sel()[0].begin()
		scope_name = (v.scope_name(pt).rstrip())

		v.set_read_only(False)

		if action == 'insert_line':
			self.insert_text(edit)

		elif action == 'insert_cb':
			self.insert_cb(edit)

		elif action == 'insert_opd_input':
			v.insert(edit, self.delta_input, text)
			self.delta_input += len(text)

		elif action == 'insert_opd_out':
			self.delta_input += len(text)
			v.insert(edit, self.view.size(), text)

		elif action == 'replace':
			v.replace(edit, Region(region[0], region[1]), text)

		elif action == 'erase':
			v.erase(edit, Region(region[0], region[1]))

		elif action == 'apply_edit_changes':
			self.apply_edit_changes()

		elif action == 'init':
			self.init(edit, run_file=run_file, build_sys=build_sys, clr_tests=clr_tests, \
				test=test, source_view_id=source_view_id, test_id=test_id, load_session=load_session)

		elif action == 'redirect_var_value':
			self.redirect_var_value(var_name, pos=pos)

		elif action == 'close':
			try:
				self.process_manager.terminate()
			except:
				print('[FastOlympicCoding] process terminating error')
			# v.run_command('test_manager', {'action': 'erase_all'})

		elif action == 'redirect_frames':
			self.redirect_frames()

		elif action == 'select_frame':
			self.select_frame(frame_id)

		elif action == 'new_test':
			self.new_test(edit)

		elif action == 'toggle_new_test':
			self.toggle_new_test()
		
		elif action == 'delete_tests':
			self.delete_tests(edit)

		elif action == 'accept_test':
			self.set_tests_status()

		elif action == 'decline_test':
			self.set_tests_status(accept=False)

		elif action == 'erase_all':
			v.replace(edit, Region(0, v.size()), '\n')

		elif action == 'show_text':
			v.replace(edit, Region(0, v.size()), self.text_buffer)
			v.sel().clear()
			v.sel().add(Region(v.size(), v.size()))

		elif action == 'hide_text':
			self.text_buffer = v.substr(Region(0, v.size()))
			self.sel_buffer = v.sel()
			v.run_command('test_manager', {'action':'erase_all'})

		elif action == 'kill_proc':
			self.tester.terminate()

		elif action == 'sync_read_only':
			self.sync_read_only()

		elif action == 'enable_edit_mode':
			self.enable_edit_mode()
			return

		elif action == 'toggle_using_debugger':
			self.use_debugger = not self.use_debugger
			if (self.use_debugger):
				sublime.status_message('debugger enabled')
			else:
				sublime.status_message('debugger disabled')

		elif action == 'set_cursor_to_end':
			v.sel().clear()
			v.sel().add(Region(v.size(), v.size()))

		self.sync_read_only()

	def isEnabled(view, args):
		pass

class EditModifyListener(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		if view.settings().get('edit_mode'):
			if view.size() == 0:
				view.run_command('test_edit', {
					'action': 'replace',
					'region': [0, view.size()],
					'text': '\n'
				})

			mod = []
			change = False
			for reg in view.sel():
				if reg.a == 0:
					change = True
				mod.append(Region(max(reg.a, 1), max(reg.b, 1)))

			if change:
				view.sel().clear()
				view.sel().add_all(mod)
