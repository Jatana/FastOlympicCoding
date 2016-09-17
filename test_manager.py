import sublime, sublime_plugin
import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
import shlex
from sublime import Region
from os import path
from importlib import import_module

from FastOlympicCoding.Modules.ProcessManager import ProcessManager
from FastOlympicCoding.Modules import basics
from FastOlympicCoding.settings import root_dir, plugin_name, run_options
from FastOlympicCoding.Engine import SysManager
from FastOlympicCoding.debuggers import debugger_info
from FastOlympicCoding.Highlight.CppVarHighlight import highlight


class TestManagerCommand(sublime_plugin.TextCommand):
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

	use_debugger = True

	# Test
	#REGION_POS_PROP = REGION_UNKNOWN_PROP


	class Test(object):
		"""
		class for tests buffer
		continues data of start, end, correct and uncorrect answers
		"""
		def __init__(self, prop, start=None, end=None):
			super(TestManagerCommand.Test, self).__init__()
			if type(prop) == str:
				self.test_string = prop
				self.correct_answers = set()
				self.uncorrect_answers = set()
			else:
				self.test_string = prop['test']
				self.correct_answers = set(prop.get('correct_answers', set()))
				self.uncorrect_answers = set(prop.get('uncorrect_answers', set()))

			self.start = start
			self.end = end


		def add_correct_answer(self, answer):
			self.correct_answers.add(answer.lstrip().rstrip())

		def add_uncorrect_answer(self, answer):
			self.uncorrect_answers.add(answer.lstrip().rstrip())

		def remove_correct_answer(self, answer):
			'''
			removes correct answer no except
			'''
			answer = answer.lstrip().rstrip()
			if answer in self.correct_answers:
				self.correct_answers.remove(answer)

		def remove_uncorrect_answer(self, answer):
			'''
			removes uncorrect answer no except
			'''
			answer = answer.lstrip().rstrip()
			if answer in self.uncorrect_answers:
				self.uncorrect_answers.remove(answer)

		def is_correct_answer(self, answer):
			answer = answer.rstrip().lstrip()
			if answer in self.correct_answers:
				return True
			if answer in self.uncorrect_answers:
				return False
			return None

		def append_string(self, s):
			self.test_string += s

		def set_inner_range(self, start, end):
			self.start = start
			self.end = end

		def memorize(self):
			d = {'test': self.test_string}
			if self.correct_answers:
				d['correct_answers'] = list(self.correct_answers)
			if self.uncorrect_answers:
				d['uncorrect_answers'] = list(self.uncorrect_answers)
			return d

		def __str__(self):
			return self.test_string

	class Tester(object):
		"""
		class for manage tests
		"""
		def __init__(self, process_manager, \
			on_insert, on_out, on_stop, on_status_change, \
			sync_out=False, tests=[]):
			super(TestManagerCommand.Tester, self).__init__()
			self.process_manager = process_manager
			self.sync_out = sync_out
			self.tests = tests
			self.test_iter = 0
			self.on_insert = on_insert
			self.on_out = on_out
			self.on_stop = on_stop
			self.proc_run = False
			self.prog_out = []
			if type(self.process_manager) != ProcessManager:
				self.process_manager.set_calls(self.__on_out, self.__on_stop, on_status_change)

		def __on_stop(self, rtcode, crash_line=None):
			self.proc_run = False
			self.test_iter += 1
			self.on_stop(rtcode, crash_line=crash_line)

		def __on_out(self, s):
			n = self.test_iter
			self.prog_out[n] += s
			self.on_out(s)

		def __pipe_listener(self, pipe, on_out, bfsize=None):
			'''
			wait for PIPE out 
			and calls on_out(`out`)
			'''
			return "!INDEV\n"

		def __process_listener(self):
			'''
			wait for process out or died and 
			calls callbacks on_out, on_stop
			'''
			proc = self.process_manager
			while proc.is_stopped() is None:
				if self.sync_out:
					s = proc.read(bfsize=4096)
				else:
					s = proc.read()
				self.__on_out(s)
			try:
				s = proc.read()
				self.__on_out(s)
			except:
				'output already putted'
			self.proc_run = False
			self.test_iter += 1
			self.on_stop(proc.is_stopped())

		def insert(self, s, call_on_insert=False):
			n = self.test_iter
			if self.proc_run:
				# self.on_insert(s)
				self.tests[n].append_string(s)
				self.process_manager.write(s)
				if call_on_insert:
					self.on_insert(s)

		def insert_test(self):
			n = self.test_iter
			tests = self.tests
			if n == 0:
				self.process_manager.compile()
			if n < len(tests):
				self.process_manager.run()
				self.proc_run = True
				self.process_manager.write(tests[n].test_string)
				self.on_insert(tests[n].test_string)

		def next_test(self):
			n = self.test_iter
			tests = self.tests
			prog_out = self.prog_out
			if n >= len(tests):
				tests.append(TestManagerCommand.Test(''))
			if n >= len(prog_out):
				prog_out.append('')
			self.insert_test()
			if type(self.process_manager) == ProcessManager:
				sublime.set_timeout_async(self.__process_listener)

		def have_pretests(self):
			n = self.test_iter
			tests = self.tests
			return n < len(tests)

		def get_tests(self):
			return self.tests

		def del_test(self, nth):
			self.test_iter -= 1
			self.tests.pop(nth)
			self.prog_out.pop(nth)

		def del_tests(self, to_del):
			dont_add = set(to_del)
			tests = self.tests
			out = self.prog_out
			new_tests = []
			new_out = []
			for i in range(len(tests)):
				if not i in dont_add:
					new_tests.append(tests[i])
					new_out.append(out[i])

			self.prog_out = new_out
			self.tests = new_tests
			self.test_iter -= len(to_del)

		def accept_out(self, nth):
			'''
			accepts current out
			'''
			outs = self.prog_out
			tests = self.tests
			if nth >= len(outs):
				'''
				Program not tested on this test
				'''
				return None
			tests[nth].add_correct_answer(outs[nth].rstrip().lstrip())
			tests[nth].remove_uncorrect_answer(outs[nth].rstrip().lstrip())

		def decline_out(self, nth):
			'''
			declines current out
			'''
			outs = self.prog_out
			tests = self.tests
			if nth >= len(outs):
				'''
				Program not tested on this test
				'''
				return None
			tests[nth].remove_correct_answer(outs[nth].rstrip().lstrip())
			tests[nth].add_uncorrect_answer(outs[nth].rstrip().lstrip())

		def check_test(self, nth):
			return self.tests[nth].is_correct_answer(self.prog_out[nth])

		def terminate(self):
			self.process_manager.terminate()


	def insert_text(self, edit, text=None):
		v = self.view
		if text is None:
			if not self.tester.proc_run:
				return None
			to_shove = v.substr(Region(self.delta_input, v.size()))
			print('shovel -> ', to_shove)
			v.insert(edit, v.size(), '\n')

		else:
			to_shove = text
			v.insert(edit, v.size(), to_shove + '\n')
		self.delta_input = v.size()
		self.tester.insert(to_shove + '\n')

	def insert_cb(self, edit):
		v = self.view
		s = sublime.get_clipboard()
		lst = s.split('\n')
		for i in range(len(lst) - 1):
			self.tester.insert(lst[i] + '\n', call_on_insert=True)
		self.tester.insert(lst[-1], call_on_insert=True)

	def new_test(self, edit):
		v = self.view
		v.insert(edit, self.view.size(), \
				(self.BEGIN_TEST_STRING + '\n') % (self.tester.test_iter + 1))

		v.add_regions(self.REGION_BEGIN_KEY % self.tester.test_iter, \
			[Region(v.line(v.size() - 2).begin(), v.line(v.size() - 2).begin() + 1)], \
				*self.REGION_POS_PROP)

		self.delta_input = v.size()
		self.out_region_set = False
		v.insert(edit, self.view.size(), self.OUT_TEST_STRING)
		# v.add_regions(self.REGION_OUT_KEY % (self.tester.test_iter + 1), \
		# 	[sublime.Region(v.size() - 2, v.size() - 2)], *self.REGION_OUT_PROP)
		self.tester.next_test()
		# v.window().active_view().set_status('process_status', 'Process Run')
		if self.tester.test_iter > 4:
			self.fold_accept_tests()



	def memorize_tests(self):
		# print([x.memorize() for x in (self.tester.get_tests())])
		f = open(self.dbg_file + ':tests', 'w')
		f.write(sublime.encode_value([x.memorize() for x in (self.tester.get_tests())], True))
		f.close()

	def on_insert(self, s):
		self.view.run_command('test_manager', {'action': 'insert_opd_input', 'text': s})

	def on_out(self, s):
		v = self.view

		self.view.run_command('test_manager', {'action': 'insert_opd_out', 'text': s})
		if not self.out_region_set:
			v.add_regions(self.REGION_OUT_KEY % (self.tester.test_iter + 1), \
				[sublime.Region(v.size() - 1, v.size() - 1)], *self.REGION_OUT_PROP)
			self.out_region_set = True

	def on_stop(self, rtcode, crash_line=None):
		v = self.view
		self.view.run_command('test_manager', {'action': 'insert_opd_out', \
			'text': (('\n' + self.END_TEST_STRING + '\n') % str(rtcode))})
		v.add_regions("test_end_%d" % (self.tester.test_iter - 1), \
			[Region(v.line(v.size() - 2).begin(), v.line(v.size() - 2).begin() + 1)], \
				*self.REGION_POS_PROP)
		tester = self.tester
		# self.view.erase_status('process_status')
		if str(rtcode) == '0':
			if tester.have_pretests():
				self.view.run_command('test_manager', {'action': 'new_test'})
			else:
				self.memorize_tests()
		# print(self.tester.prog_out)
		cur_test = self.tester.test_iter - 1
		check = self.tester.check_test(cur_test)
		if check:
			self.set_test_status(cur_test, accept=True, call_tester=False)
		elif check is False:
			self.set_test_status(cur_test, accept=False, call_tester=False)
		else:
			self.set_test_status(cur_test, accept=None, call_tester=False)

		# add crash regions
		if crash_line is not None:
			for x in v.window().views():
				if x.id() == self.code_view_id:
					#print('setbryak ->', crash_line)
					x.run_command('view_tester', {'action': 'show_crash_line', 'crash_line': crash_line})

	def redirect_var_value(self, var_name):
		view = self.view
		print('VarName:', var_name)
		value = self.tester.process_manager.get_var_value(var_name)
		print(value)
		for x in view.window().views():
			if x.id() == self.code_view_id:
				x.run_command('view_tester', {'action': 'show_var_value', 'value': value})



	def toggle_side_bar(self):
		self.view.window().run_command('toggle_side_bar')

	def set_test_status(self, nth, accept=True, call_tester=True):
		v = self.view
		beg_key = self.REGION_BEGIN_KEY % nth
		rs = v.get_regions(beg_key)[0]
		v.erase_regions(beg_key)
		if accept:
			prop = self.REGION_ACCEPT_PROP
			if call_tester:
				self.tester.accept_out(nth)
		elif accept is False:
			prop = self.REGION_DECLINE_PROP
			if call_tester:
				self.tester.decline_out(nth)
		else:
			prop = self.REGION_UNKNOWN_PROP

		#prop = self.get_style_test_status(nth)
		v.add_regions(beg_key, [rs], *prop)

	def set_tests_status(self, accept=True):
		v = self.view
		sels = v.sel()
		cur_test = self.tester.test_iter
		for i in range(cur_test):
			begin_key = self.REGION_BEGIN_KEY % i
			rs_beg = v.get_regions(begin_key)[0]
			beg = rs_beg.begin()

			end_key = self.REGION_END_KEY % i
			rs_end = v.get_regions(end_key)[0]
			end = v.line(rs_end.begin()).end()
			r = Region(beg, end)
			for x in sels:
				if x.intersects(r):
					self.set_test_status(i, accept=accept)
		self.memorize_tests()

	def fold_accept_tests(self):
		v = self.view
		cur_test = self.tester.test_iter
		for i in range(cur_test):
			if self.tester.check_test(i):
				beg = v.get_regions(self.REGION_BEGIN_KEY % i)[0].begin()
				end = v.line(v.get_regions(self.REGION_END_KEY % i)[0].begin()).end()
				v.fold(Region(v.word(beg + 5).end(), end))

	def change_process_status(self, status):
		self.view.set_status('process_status', status)

	def make_opd(self, edit, run_file=None, build_sys=None, clr_tests=False, \
		sync_out=False, code_view_id=None):
		v = self.view
		v.set_scratch(True)
		v.set_status('opd_info', 'opdebugger-file')
		v.run_command('test_manager', {'action': 'erase_all'})
		self.dbg_file = run_file
		self.code_view_id = code_view_id
		if not v.settings().get('word_wrap'):
			v.run_command('toggle_setting', {"setting": "word_wrap"})
		# if SysManager.is_sidebar_open(v.window()):
			# sublime.set_timeout(self.toggle_side_bar, 500)
		if not clr_tests:
			try:
				f = open(run_file + ':tests')
				tests = [self.Test(x) for x in sublime.decode_value(f.read())]
				f.close()
			except:
				tests = []
		else:
			f = open(run_file + ':tests', 'w')
			f.write('[]')
			f.close()
			tests = []
		file_ext = path.splitext(run_file)[1][1:]
		DebugModule = debugger_info.get_best_debug_module(file_ext) #self.have_debugger(file_ext)
		# if DebugModule is None:
		if (not self.use_debugger) or (DebugModule is None):
			process_manager = ProcessManager(run_file, build_sys, run_options=run_options)
		else:
			print(DebugModule)
			process_manager = DebugModule(run_file)
		sublime.set_timeout_async(lambda :self.change_process_status('COMPILING'))
		cmp_data = process_manager.compile()
		print('compile: data', type(cmp_data))
		if cmp_data is None or cmp_data[0] == 0:
			self.tester = self.Tester(process_manager, \
				self.on_insert, self.on_out, self.on_stop, self.change_process_status, \
				tests=tests, sync_out=sync_out)
			v.run_command('test_manager', {'action': 'new_test'})
			# v.set_status('process_status', 'Process Run')
		else:
			v.insert(edit, 0, cmp_data[1])
			#v.run_command('test_manager', {'action': 'insert_opd_out', 'text': cmp_data[1]})

	def delete_nth_test(self, edit, nth, fixed_end=None):
		'''
		deletes nth test
		and NOT reNumerating other tests ID
		'''
		v = self.view
		begin = v.get_regions(self.REGION_BEGIN_KEY % nth)[0].begin()
		if fixed_end is not None:
			end = fixed_end
		else:
			end = v.line(v.get_regions(self.REGION_END_KEY % nth)[0].begin()).end() + 1
		v.replace(edit, Region(begin, end), '')
		v.erase_regions(self.REGION_BEGIN_KEY % nth)
		v.erase_regions(self.REGION_END_KEY % nth)

	def get_style_test_status(self, nth):
		check = self.tester.check_test(nth)
		if check:
			return self.REGION_ACCEPT_PROP
		elif check is False:
			return self.REGION_DECLINE_PROP
		return self.REGION_UNKNOWN_PROP

	def renumerate_tests(self, edit, max_nth_test):
		'''
		renumerating tests
		sample if 
			[test 2, test 5] -> [test 1, test 2]
		uses after del_tests
		'''
		v = self.view
		cur_nth = 0
		for i in range(0, max_nth_test):
			begin_key = self.REGION_BEGIN_KEY % i
			rs_beg = v.get_regions(begin_key)
			if rs_beg:
				rs_beg = rs_beg[0]
				v.replace(edit, v.word(rs_beg.begin() + 5), str(cur_nth + 1))
				v.erase_regions(begin_key)
				v.add_regions(self.REGION_BEGIN_KEY % (cur_nth), [rs_beg], \
					*self.get_style_test_status(cur_nth))

				end_key = self.REGION_END_KEY % i
				rs_end = v.get_regions(end_key)
				if rs_end:
					rs_end = rs_end[0]
					v.erase_regions(end_key)
					v.add_regions(self.REGION_END_KEY % (cur_nth), [rs_end], \
						*self.REGION_POS_PROP)

				cur_nth += 1


	def delete_tests(self, edit):
		v = self.view
		cur_test = self.tester.test_iter
		if self.tester.proc_run:
			v.add_regions('delta_input', [Region(self.delta_input, self.delta_input + 1)], \
				'', '', sublime.HIDDEN)

		sels = v.sel()
		if self.tester.proc_run:
			end_tbegin = v.get_regions(self.REGION_BEGIN_KEY % cur_test)[0].begin()
			for x in sels:
				if x.end() >= end_tbegin:
					self.tester.terminate()
					self.delete_nth_test(edit, cur_test, fixed_end=v.size())
					cur_test -= 1
					break
		to_del = []
		for i in range(cur_test):
			begin = v.get_regions(self.REGION_BEGIN_KEY % i)[0].begin()
			end = v.line(v.get_regions(self.REGION_END_KEY % i)[0].begin()).end()
			r = Region(begin, end)
			for x in sels:
				if x.intersects(r):
					to_del.append(i)
		# print('deleted -> ', ' '.join(map(str, to_del)))
		sublime.status_message('deleted tests: ' + (', '.join(map(lambda x: str(x + 1), to_del))))
		self.tester.del_tests(to_del)
		for x in to_del:
			self.delete_nth_test(edit, x)
		self.renumerate_tests(edit, cur_test + 2)
		if self.tester.proc_run:
			self.delta_input = v.get_regions('delta_input')[0].begin()
		self.memorize_tests()

	def sync_read_only(self):
		view = self.view
		have_sel_no_end = False
		for sel in view.sel():
			# print(sel.begin(), view.size())
			if sel.begin() != view.size():
				have_sel_no_end = True
				break

		view.set_read_only(have_sel_no_end)


	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False, \
			sync_out=False, code_view_id=None, var_name=None):
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
			v.insert(edit, self.view.size(), text)

		elif action == 'make_opd':
			self.make_opd(edit, run_file=run_file, build_sys=build_sys, clr_tests=clr_tests, \
				sync_out=sync_out, code_view_id=code_view_id)

		elif action == 'redirect_var_value':
			self.redirect_var_value(var_name)

		elif action == 'close':
			try:
				self.process_manager.terminate()
			except:
				print('Error When terminating process')
			v.run_command('test_manager', {'action': 'erase_all'})

		elif action == 'new_test':
			self.new_test(edit)
		
		elif action == 'delete_tests':
			self.delete_tests(edit)

		elif action == 'accept_test':
			self.set_tests_status()

		elif action == 'decline_test':
			self.set_tests_status(accept=False)

		elif action == 'erase_all':
			v.replace(edit, Region(0, v.size()), '')

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

		elif action == 'toggle_using_debugger':
			self.use_debugger ^= 1
			if (self.use_debugger):
				sublime.status_message('debugger enabled')
			else:
				sublime.status_message('debugger disabled')
		self.sync_read_only()

	def isEnabled(view, args):
		print(view)


class ModifiedListener(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		if view.get_status('opd_info') == 'opdebugger-file':
			if len(view.sel()) > 0:
				if view.substr(view.sel()[0]) == 'Test':
					view.sel().clear()
					def show_test_menu():
						view.show_popup_menu(['Delete'], lambda x: print(x))

					sublime.set_timeout(show_test_menu, 100)

			view.run_command('test_manager', {'action': 'sync_read_only'})

	# def on_window_command(self, window, cmd, args):
	# 	if cmd == 'toggle_side_bar':
	# 		print('mi togli!')



get_syntax = basics.get_syntax
supports_langs = {basics.CLANG, basics.PYTHON, basics.PASCAL}
OPD_LANG = basics.OPDebugger
class CloseListener(sublime_plugin.EventListener):
	"""Listen to Close"""
	def __init__(self):
		super(CloseListener, self).__init__()

	def on_pre_close(self, view):
		if get_syntax(view) == OPD_LANG:
			view.run_command('test_manager', {'action': 'close'})
			print("specclose")
		# print('closed')


class ViewTesterCommand(sublime_plugin.TextCommand):
	ROOT = dirname(__file__)
	ruler_opd_panel = 0.75
	have_tied_dbg = False

	def create_opd(self, clr_tests=False, sync_out=True):
		'''
		creates opd with supported language
		'''
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		file_name = v.file_name()
		file_ext = path.splitext(file_name)[1][1:]
		# v.window().show_input_panel("Runned", "123", \
		# 	self.DebugArea.on_done, self.DebugArea.on_change, self.DebugArea.on_cancel)
		# v.window().show_quick_panel(["5"], \
		# 	1, 1, 1, 1)
		#print('windowshe4ka generat')
		window = v.window()
		v.erase_regions('crash_line')
		# opd_view = window.create_output_panel("opd_view")
		# print(opd_view.settings().get('syntax'))
		# window.run_command('show_panel', {'panel': 'output.opd_view'})
		if self.have_tied_dbg:
			prop = (window.get_view_index(self.tied_dbg))
			if prop == (-1, -1):
				need_new = True
			else:
				need_new = False
		else:
			need_new = True

		if not need_new:
			dbg_view = self.tied_dbg
			create_new = False
		else:
			dbg_view = window.new_file()
			self.tied_dbg = dbg_view
			self.have_tied_dbg = True
			create_new = True
			dbg_view.run_command('toggle_setting', {"setting": "line_numbers"})
			# dbg_view.run_command('toggle_setting', {"setting": "gutter"})
			try:
				sublime.set_timeout_async(lambda window=window: window.set_sidebar_visible(False), 50)
			except:
				# Version of sublime text < 3102
				pass
			dbg_view.run_command('toggle_setting', {"setting": "word_wrap"})

		window.set_layout({
			"cols": [0, self.ruler_opd_panel, 1],
			"rows": [0, 1],
			"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
		})
		window.set_view_index(dbg_view, 1, 0)
		window.focus_view(v)
		window.focus_view(dbg_view)
		# opd_view.run_command('erase_view')
		dbg_view.set_syntax_file('Packages/%s/OPDebugger.tmLanguage' % plugin_name)
		dbg_view.set_name(os.path.split(v.file_name())[-1] + ' -run')
		dbg_view.run_command('test_manager', \
			{'action': 'make_opd', 'build_sys': file_syntax, 'run_file': v.file_name(), \
			"clr_tests": clr_tests, "sync_out": sync_out, 'code_view_id': v.id()})
	
	def close_opds(self):
		w = self.view.window()
		for v in w.views():
			if v.get_status('opd_info') == 'opdebugger-file':
				v.close()

	def get_var_value(self):
		view = self.view
		pt = view.sel()[0].begin()
		var_name = view.substr(view.word(pt))
		if self.have_tied_dbg:
			dbg = self.tied_dbg
			dbg.run_command('test_manager', {'action' : 'redirect_var_value', 'var_name': var_name})

	def show_var_value(self, value):
		print(value)
		self.view.show_popup(highlight(value))


	def run(self, edit, action=None, clr_tests=False, text=None, sync_out=True, crash_line=None, value=None):
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		if action == 'insert':
			v.insert(edit, v.sel()[0].begin(), text)
		elif action == 'make_opd':
			self.close_opds()
			self.create_opd(clr_tests=clr_tests, sync_out=sync_out)
		elif action == 'show_crash_line':
			pt = v.text_point(crash_line - 1, 0)
			v.erase_regions('crash_line')
			v.add_regions('crash_line', [sublime.Region(pt + 0, pt + 0)], \
				'variable.language.python', 'bookmark', \
				sublime.DRAW_SOLID_UNDERLINE)
			sublime.set_timeout_async(lambda pt=pt: v.show_at_center(pt), 39)
			# print(pt)
		elif action == 'get_var_value':
			self.get_var_value()

		elif action == 'show_var_value':
			self.show_var_value(value)

		elif action == 'sync_opdebugs':
			w = v.window()
			layout = w.get_layout()

			def slow_hide(w=w, layout=layout):
				if layout['cols'][1] < 1:
					layout['cols'][1] += 0.001
					w.set_layout(layout)
					sublime.set_timeout(slow_hide, 1)
				else:
					layout['cols'][1] = 1
					w.set_layout(layout)
					print('stopped')

			if len(layout['cols']) == 3:
				if layout['cols'][1] != 1:
					# hide opd panel
					self.ruler_opd_panel = min(layout['cols'][1], 0.93)
					layout['cols'][1] = 1
					# <This Region May be uncomment>
					#for x in w.views_in_group(1):
					#	x.run_command('test_manager', {'action': 'hide_text'})
					# < / >
					# slow_hide()
					w.set_layout(layout)
				else:
					# show opd panel
					layout['cols'][1] = self.ruler_opd_panel
					need_x = self.ruler_opd_panel
					# < This Region May be uncomment >
					#for x in w.views_in_group(1):
					#	x.run_command('test_manager', {'action': 'show_text'})
					# < / >
					w.set_layout(layout)
			# w.run_command('toggle_side_bar')
			


class LayoutListener(sublime_plugin.EventListener):
	"""docstring for LayoutListener"""
	def __init__(self):
		super(LayoutListener, self).__init__()
	
	def move_syncer(self, view):
		try:
			w = view.window()
			prop = w.get_view_index(view)
			print(view.name())
			if view.name()[-4:] == '-run':
				w.set_view_index(view, 1, 0)
				print('moved to second group')
			elif prop[0] == 1:
				active_view_index = w.get_view_index(w.active_view_in_group(0))[1]
				print('moved to first group')
				w.set_view_index(view, 0, active_view_index + 1)
		except:
			pass
		

	def on_load(self, view):
		self.move_syncer(view)

	def on_new(self, view):
		self.move_syncer(view)
