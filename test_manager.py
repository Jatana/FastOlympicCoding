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
from .settings import base_name, get_settings, root_dir, get_tests_file_path
from .debuggers import debugger_info
from .ContestHandlers import handler_info
from .Highlight.CppVarHighlight import highlight
from .Highlight.test_interface import get_test_styles


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
	REGION_BEGIN_PROP = ['string', 'Packages/' + base_name + '/icons/arrow_right.png', \
				sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE | \
					sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY_AS_OVERWRITE]
	REGION_END_PROP = ['variable.c++', 'Packages/' + base_name + '/icons/arrow_left.png', sublime.HIDDEN]
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
		self.test_phantoms = [PhantomSet(view, 'test-phantoms-' + str(i)) for i in range(10)]

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
			self.fold = True
			self.end = end
			self.runtime = '-'

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

		def set_tie_pos(self, pos):
			self.tie_pos = pos

		def set_cur_runtime(self, runtime):
			self.runtime = runtime

		def set_cur_rtcode(self, rtcode):
			self.rtcode = rtcode

		def get_nice_runtime(self):
			runtime = self.runtime
			if runtime < 5000:
				return '&nbsp;' * (2 - len(str(self.runtime))) + str(runtime) + 'ms'
			else:
				return str(runtime // 1000) + 's'

		def get_config(self, i, pt, _cb_act, _out, view, running=False):	
			if not running:
				styles = get_test_styles(view)
				content = open(root_dir + '/Highlight/test_config.html').read()
				test_type = ''
				if self.is_correct_answer(_out):
					test_type = 'test-accept'

				if str(self.rtcode) != '0':
					test_type = 'test-decline'

				content = content.format(
					test_id=i,
					runtime=self.get_nice_runtime(),
					test_type=test_type
				)
				content = '<style>' + styles + '</style>' + content

				def onclick(event, cb=_cb_act, i=i):
					_cb_act(i, event)

				phantom = Phantom(Region(pt), content, sublime.LAYOUT_BLOCK, onclick)
				return phantom
			else:
				styles = get_test_styles(view) 
				content = open(root_dir + '/Highlight/test_running.html').read()
				content = content.format(
					test_id=i
				)
				content = '<style>' + styles + '</style>' + content
				def onclick(event, cb=_cb_act, i=i):
					_cb_act(i, event)

				phantom = Phantom(Region(pt), content, sublime.LAYOUT_BLOCK, onclick)
				return phantom

		def get_accdec(self, i, pt, _cb_act, type, _view):	
			styles = get_test_styles(_view)
			content = open(root_dir + '/Highlight/test_accdec.html').read()
			content = content.format(
				test_id=i,
				type=type,
				runtime='&nbsp;' * (2 - len(str(self.runtime))) + str(self.runtime)
			)
			content = '<style>' + styles + '</style>' + content

			def onclick(event, cb=_cb_act, i=i):
				_cb_act(i, event)

			phantom = Phantom(Region(pt), content, sublime.LAYOUT_BLOCK, onclick)
			return phantom

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
			self.running_test = None
			self.running_new = None
			self.on_insert = on_insert
			self.on_out = on_out
			self.on_stop = on_stop
			self.proc_run = False
			self.prog_out = []
			self.on_status_change = on_status_change
			if type(self.process_manager) != ProcessManager:
				self.process_manager.set_calls(self.__on_out, self.__on_stop, on_status_change)

		def __on_stop(self, rtcode, runtime=-1, crash_line=None):
			self.prog_out[self.running_test] = self.prog_out[self.running_test].rstrip()
			self.proc_run = False

			if self.running_new:
				self.test_iter += 1

			if type(self.process_manager) == ProcessManager:
				self.on_status_change('STOPPED')

			self.on_stop(rtcode, runtime, crash_line=crash_line)

		def __on_out(self, s):
			n = self.running_test
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
			start_time = time()
			while proc.is_stopped() is None:
				if self.sync_out:
					s = proc.read(bfsize=1)
				else:
					s = proc.read()
				self.__on_out(s)
			try:
				s = proc.read()
				self.__on_out(s)
			except:
				'output already putted'
			runtime = int((time() - start_time) * 1000)
			self.__on_stop(proc.is_stopped(), runtime)

		def insert(self, s, call_on_insert=False):
			n = self.running_test
			if self.proc_run:
				# self.on_insert(s)
				self.tests[n].append_string(s)
				self.process_manager.write(s)
				if call_on_insert:
					self.on_insert(s)

		def insert_test(self, id=None):
			if id is None:
				id = self.test_iter
			# n = self.test_iter
			tests = self.tests

			if type(self.process_manager) == ProcessManager:
				self.on_status_change('RUNNING')
				
			self.proc_run = True
			self.process_manager.run()
			self.process_manager.write(tests[id].test_string)
			self.on_insert(tests[id].test_string)

		def next_test(self, tie_pos, cb):
			n = self.test_iter
			tests = self.tests
			prog_out = self.prog_out

			if self.proc_run:
				sublime.status_message('process already running')
				return

			if n >= len(tests):
				tests.append(TestManagerCommand.Test(''))
			if n >= len(prog_out):
				prog_out.append('')
			tests[n].set_tie_pos(tie_pos)
			self.running_test = n
			self.running_new = True

			def go(self=self, cb=cb):
				self.insert_test()
				if type(self.process_manager) == ProcessManager:
					sublime.set_timeout_async(self.__process_listener)
				cb()

			sublime.set_timeout_async(go, 10)

		def run_test(self, id):
			tests = self.tests
			process_manager = self.process_manager
			self.on_status_change('COMPILE')
			process_manager.compile()
			self.running_test = id
			self.running_new = False
			self.prog_out[id] = ''
			self.insert_test(id)
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

		def set_tests(self, tests):
			self.tests.clear()
			for test in tests:	
				self.tests.append(TestManagerCommand.Test(test))

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
		expected = v.line(self.delta_input).end()
		if len(v.sel()) > 1: return
		if v.sel()[0].a != expected or v.sel()[0].b != expected: return
		if text is None:
			if not self.tester.proc_run:
				return None
			to_shove = v.substr(Region(self.delta_input, v.sel()[0].b))
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

	def toggle_fold(self, i):
		v = self.view
		tester = self.tester

		_inp = self.tester.tests[i].test_string
		_outp = self.tester.prog_out[i]
		text = _inp + '\n' + _outp.rstrip() + '\n' + '\n'
		tie_pos = self.get_tie_pos(i)

		if tester.tests[i].fold:
			v.run_command('test_manager', {
				'action': 'replace',
				'region': (tie_pos + 1, tie_pos + 1),
				'text': text
			})

			v.add_regions(self.REGION_BEGIN_KEY % i, \
				[Region(tie_pos + 1)], *self.REGION_BEGIN_PROP)

			v.add_regions('test_end_%d' % i, \
				[Region(tie_pos + len(_inp) + 2, tie_pos + len(_inp) + 2)], \
					*self.REGION_END_PROP)

			d = len(text)
			for j in range(i + 1, self.tester.test_iter):
				self.tester.tests[j].tie_pos += d

			tester.tests[i].fold = False
		else:
			v.run_command('test_manager', {
				'action': 'replace',
				'region': (tie_pos + 1, tie_pos + 1 + len(text)),
				'text': ''
			})

			v.erase_regions(self.REGION_BEGIN_KEY % i)
			v.erase_regions('test_end_%d' % i)

			d = len(text)
			for j in range(i + 1, tester.test_iter):
				tester.tests[j].tie_pos -= d

			tester.tests[i].fold = True
		v.sel().clear()
		v.sel().add(Region(v.size()))
		self.update_configs()

	def open_test_edit(self, i):
		v = self.view
		tester = self.tester
		v.window().focus_group(1)
		edit_view = v.window().new_file()
		v.window().set_view_index(edit_view, 1, 1)
		edit_view.run_command('test_edit', {
			'action': 'init',
			'test_id': i,
			'test': tester.tests[i].test_string,
			'source_view_id': v.id()
		})

	def get_tie_pos(self, i):
		v = self.view
		tester = self.tester
		pt = 0
		for j in range(i):
			running = tester.proc_run and j == tester.running_test

			if running:
				pt += len(tester.tests[j].test_string) + len(tester.prog_out[j]) + 1 
			elif not tester.tests[j].fold:
				pt += len(tester.tests[j].test_string) + len(tester.prog_out[j]) + 1

			if not tester.tests[j].fold:
				pt += 2

		return pt

	def on_test_action(self, i, event):
		v = self.view
		tester = self.tester
		if tester.proc_run and event in {'test-click', 'test-edit', 'test-run'}:
			sublime.status_message('can not {action} while process running'.format(action=event))
			return
		if event == 'test-click':	
			self.toggle_fold(i)	
		elif event == 'test-edit':
			self.open_test_edit(i)
		elif event == 'test-stop':
			tester.terminate()
		elif event == 'test-run':
			if not tester.tests[i].fold:
				self.toggle_fold(i)
			tie_pos = self.get_tie_pos(i)
			v.run_command('test_manager', {
				'action': 'replace',
				'region': (tie_pos, tie_pos),
				'text': '\n\n'
			})
			v.add_regions('type', \
				[Region(tie_pos + 1)], *self.REGION_BEGIN_PROP)

			self.input_start = tie_pos + 1
			self.delta_input = tie_pos + 1

			v.sel().clear()
			v.sel().add(Region(tie_pos + 1))

			self.prepare_code_view()

			tester.run_test(i)	
			self.update_configs()

	def on_accdec_action(self, i, event):
		v = self.view
		tester = self.tester
		if event == 'click-accept':
			tester.accept_out(i)
		elif event == 'click-decline':
			tester.decline_out(i)
		self.update_configs()
		self.memorize_tests()

	def set_test_input(self, test=None, id=None):
		v = self.view
		tester = self.tester
		unfold = False
		if not tester.tests[id].fold:
			self.toggle_fold(id)
			unfold = True

		tester.tests[id].test_string = test

		if unfold:
			self.toggle_fold(id)

		self.memorize_tests()

	def get_next_title(self):
		v = self.view
		styles = get_test_styles(v) 
		content = open(root_dir + '/Highlight/test_next.html').read()

		content = '<style>' + styles + '</style>' + content

		def onclick(event, v=v):
			v.run_command('test_manager', {
				'action': 'new_test'
			})	

		phantom = Phantom(Region(self.view.size() - 1), content, sublime.LAYOUT_BLOCK, onclick)
		return phantom

	def update_configs(self, update_last=None):
		v = self.view
		tester = self.tester
		configs = []
		if tester.proc_run:
			k = tester.test_iter + 1
		else:
			k = tester.test_iter
		k = min(k, len(tester.tests))
		pt = 0
		_last_test_entry = -1
		for i in range(k):
			running = tester.proc_run and i == tester.running_test

			config = tester.tests[i].get_config(
				i,
				pt,
				self.on_test_action,
				tester.prog_out[i],
				self.view,
				running=running
			)
			_last_test_entry = len(configs)
			configs.append(config)

			if running:
				pt += len(tester.tests[i].test_string) + len(tester.prog_out[i]) + 2
			elif not tester.tests[i].fold:
				pt += len(tester.tests[i].test_string) + len(tester.prog_out[i]) + 1

			if not running and not tester.tests[i].fold and str(tester.tests[i].rtcode) == '0' and tester.prog_out[i]:
				if tester.tests[i].is_correct_answer(tester.prog_out[i]):
					type = 'decline'
				else:
					type = 'accept'
				accdec = tester.tests[i].get_accdec(
					i,
					pt,
					self.on_accdec_action,
					type,
					self.view
				)
				configs.append(accdec)

			if not tester.tests[i].fold:
				pt += 2

		if not tester.proc_run:
			configs.append(self.get_next_title())
		# self.phantoms.update(configs)

		while len(self.test_phantoms) < len(configs):
			self.test_phantoms.append(PhantomSet(v, 'test-phantom-' + str(len(self.test_phantoms))))

		hide_phantoms = v.settings().get('hide_phantoms')
		if update_last:
			self.test_phantoms[_last_test_entry].update([configs[_last_test_entry]] if not hide_phantoms else [])
		else:
			for i in range(len(configs)):
				self.test_phantoms[i].update([configs[i]] if not hide_phantoms else [])

			for i in range(len(configs), len(self.test_phantoms)):
				self.test_phantoms[i].update([])


	def new_test(self, edit):
		v = self.view

		self.input_start = v.size()
		self.delta_input = v.size()
		self.output_start = v.size() + 1
		self.out_region_set = False

		v.add_regions('type', \
			[Region(v.size(), v.size())], *self.REGION_BEGIN_PROP)

		v.sel().clear()
		v.sel().add(Region(v.size()))

		self.tester.next_test(v.size() - 1, lambda: self.update_configs(update_last=True))

		# sublime.set_timeout_async(self.update_configs)

		# self.update_configs()

		# if self.tester.test_iter > 4:
			# self.fold_accept_tests()
	
	def memorize_tests(self):
		with open(get_tests_file_path(self.dbg_file), 'w') as f:
			f.write(sublime.encode_value([x.memorize() for x in (self.tester.get_tests())], True))

	def on_insert(self, s):
		self.view.run_command('test_manager', {'action': 'insert_opd_input', 'text': s})

	def on_out(self, s):
		v = self.view

		self.view.run_command('test_manager', {'action': 'insert_opd_out', 'text': s})

		if not self.out_region_set:
			self.out_region_set = True

	def add_region(self, line, region_prop):
		v = self.view
		pos = v.line(line)
		from random import randint
		v.add_regions(str(randint(0, 1e9)), [Region(pos.a, pos.a + 1)], *region_prop)

	def on_stop(self, rtcode, runtime, crash_line=None):
		v = self.view
		tester = self.tester

		test_id = self.tester.running_test
		_inp = self.tester.tests[test_id].test_string
		_outp = self.tester.prog_out[test_id]
		_outp = _outp.rstrip()

		if tester.running_new:
			_outp += '\n' + '\n'

		self.tester.tests[test_id].set_cur_runtime(runtime)
		self.tester.tests[test_id].set_cur_rtcode(rtcode)

		v.erase_regions('type')
		line = v.line(self.input_start)

		input_end = v.line(Region(self.delta_input)).end()

		if tester.running_new and self.tester.tests[test_id].is_correct_answer(self.tester.prog_out[test_id]):
			v.run_command('test_manager', {
				'action': 'replace',
				'region': (self.input_start, input_end),
				'text': ''
			})
		else:
			v.run_command('test_manager', {
				'action': 'replace',
				'region': (self.input_start, input_end),
				'text': _inp + '\n' + _outp
			})

			self.tester.tests[test_id].fold = False

			v.add_regions(self.REGION_BEGIN_KEY % test_id, \
				[Region(line.begin(), line.end())], *self.REGION_BEGIN_PROP)

		v.show(self.input_start + 20)

		rtcode = str(rtcode)
		# if rtcode != '0':
		# 	v.run_command('test_manager', {
		# 		'action': 'insert_opd_out',
		# 		'text': '<return {rtcode}>'.format(rtcode=rtcode)
		# 	})
		# 	v.add_regions('test_error_%d' % (test_id), \
		# 		[Region(v.size() - 5, v.size() - 4)], 'variable.c++', 'dot', sublime.HIDDEN)
		# 	v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n'})

		# v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n'})

		v.add_regions('test_end_%d' % test_id, \
			[Region(self.input_start + len(_inp) + 1, self.input_start + len(_inp) + 1)], \
				*self.REGION_END_PROP)

		v.run_command('test_manager', {'action': 'set_cursor_to_end'})

		tester = self.tester
		self.memorize_tests()
		if str(rtcode) == '0':
			if tester.running_new and tester.have_pretests():
				self.update_configs(update_last=True)
				sublime.set_timeout(lambda: v.run_command('test_manager', {'action': 'new_test'}), 10)
			else:
				sublime.set_timeout(self.update_configs, 100)
		else:
			sublime.set_timeout(self.update_configs, 100)

		cur_test = tester.running_test
		check = self.tester.check_test(cur_test)

		# if check:
		# 	self.set_test_status(cur_test, accept=True, call_tester=False)
		# elif check is False:
		# 	self.set_test_status(cur_test, accept=False, call_tester=False)
		# else:
		# 	self.set_test_status(cur_test, accept=None, call_tester=False)

		# add crash regions
		if crash_line is not None:
			for x in v.window().views():
				if x.id() == self.code_view_id:
					x.run_command('view_tester', {'action': 'show_crash_line', 'crash_line': crash_line})

	def redirect_var_value(self, var_name, pos=None):
		view = self.view
		if self.tester.process_manager.has_var_view_api():
			value = self.tester.process_manager.get_var_value(var_name)
			for x in view.window().views():
				if x.id() == self.code_view_id:
					x.run_command('view_tester', {
						'action': 'show_var_value',
						'value': value,
						'pos': pos
					})

	def redirect_frames(self):
		v = self.view
		frames = self.tester.process_manager.get_frames()
		for sub in v.window().views():
			if sub.id() == self.code_view_id:
				sub.run_command('view_tester', {
					'action': 'show_frames',
					'frames': frames
				})

	def select_frame(self, id):
		self.tester.process_manager.select_frame(id)

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

	def clear_all(self):
		v = self.view
		v.run_command('test_manager', {'action': 'erase_all'})
		v.sel().clear()
		v.sel().add(Region(v.size(), v.size()))
		self.phantoms.update([])
		for phs in self.test_phantoms:
			phs.update([])
		if self.tester:
			v.erase_regions('type')
			for i in range(-1, self.tester.test_iter + 1):
				v.erase_regions(self.REGION_BEGIN_KEY % i)
				v.erase_regions(self.REGION_END_KEY % i)
				v.erase_regions('line_%d' % i)
				v.erase_regions('test_error_%d' % i)

	def set_compile_bar(self, cmd, type=''):
		view = self.view
		if type == 'error':
			type = 'config-stop'

		styles = get_test_styles(view)
		content = open(root_dir + '/Highlight/compile.html').read().format(cmd=cmd, type=type)
		content = '<style>' + styles + '</style>' + content
		phantom = Phantom(Region(0), content, sublime.LAYOUT_BLOCK)
		self.test_phantoms[0].update([phantom])

	def get_view_by_id(self, id):
		for view in self.view.window().views():
			if view.id() == id:
				return view

	def prepare_code_view(self):
		code_view = self.get_view_by_id(self.code_view_id)
		if code_view:
			if code_view.is_dirty():
				code_view.run_command('save')

	def make_opd(self, edit, run_file=None, build_sys=None, clr_tests=False, \
		sync_out=False, code_view_id=None, use_debugger=False, load_session=False):

		self.use_debugger = use_debugger
		v = self.view

		if v.get_status('process_status') == 'COMPILING':
			return

		if v.get_status('process_status') == 'RUNNING':
			print('terminating')
			self.tester.terminate()

			kwargs = {
				'run_file': run_file,
				'build_sys': build_sys,
				'clr_tests': clr_tests,
				'sync_out': sync_out,
				'code_view_id': code_view_id,
				'use_debugger': use_debugger,
				'load_session': load_session,
				'action': 'make_opd'
			}

			def rerun(kwargs=kwargs):
				v.run_command(
					'test_manager',
					kwargs
				)

			sublime.set_timeout_async(rerun, 30)
			return

		if v.settings().get('edit_mode'):
			self.apply_edit_changes()


		v.set_scratch(True)
		v.run_command('set_setting', {'setting': 'fold_buttons', 'value': False})
		v.run_command('set_setting', {'setting': 'line_numbers', 'value': False})
		v.set_status('opd_info', 'opdebugger-file')
		self.clear_all()
		if load_session:
			if self.session is None:
				v.run_command('test_manager', {'action': 'insert_opd_out', 'text': 'Can\'t restore session'})
			else:
				run_file = self.session['run_file']
				build_sys = self.session['build_sys']
				clr_tests = self.session['clr_tests']
				sync_out = self.session['sync_out']
				code_view_id = self.session['code_view_id']
				use_debugger = self.session['use_debugger']
		else:
			print('[FastOlympicCoding] session saved')
			self.session = {
				'run_file': run_file,
				'build_sys': build_sys,
				'clr_tests': clr_tests,
				'sync_out': sync_out,
				'code_view_id': code_view_id,
				'use_debugger': use_debugger
			}
			self.dbg_file = run_file
			self.code_view_id = code_view_id

		self.prepare_code_view()

		if not v.settings().get('word_wrap'):
			v.run_command('toggle_setting', {'setting': 'word_wrap'})

		if not clr_tests:
			try:
				with open(get_tests_file_path(run_file)) as f:
					tests = [self.Test(x) for x in sublime.decode_value(f.read()) if x['test'].strip()]
			except:
				tests = []
		else:
			with open(get_tests_file_path(run_file), 'w') as f:
				f.write('[]')
			tests = []
		file_ext = path.splitext(run_file)[1][1:]

		self.change_process_status('COMPILING')

		DebugModule = debugger_info.get_best_debug_module(file_ext)
		if (not self.use_debugger) or (DebugModule is None):
			process_manager = ProcessManager(
				run_file,
				build_sys,
				run_settings=get_settings().get('run_settings')
			)
		else:
			process_manager = DebugModule(run_file)

		def compile(self=self, v=v):
			cmp_data = process_manager.compile()
			self.change_process_status('COMPILED')
			self.delta_input = 0
			if cmp_data is None or cmp_data[0] == 0:
				self.tester = self.Tester(process_manager, \
					self.on_insert, self.on_out, self.on_stop, self.change_process_status, \
					tests=tests, sync_out=sync_out)
				v.settings().set('edit_mode', False)
				v.run_command('test_manager', {'action': 'new_test'})
			else:
				v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n' + cmp_data[1]})
				self.set_compile_bar('compilation error', type='error')

		self.set_compile_bar('compiling')

		sublime.set_timeout_async(compile, 10)

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
			if self.get_begin_region(nth + 1):
				end = self.get_begin_region(nth + 1)[0].begin()
			else:
				end = v.size()
			# end = v.line(v.get_regions(self.REGION_END_KEY % nth)[0].begin()).end() + 1 + 1
		v.replace(edit, Region(begin, end), '')
		v.erase_regions(self.REGION_BEGIN_KEY % nth)
		v.erase_regions(self.REGION_END_KEY % nth)
		v.erase_regions('line_%d' % nth)

	def delete_test(self, edit, id):
		v = self.view
		tester = self.tester
		if not tester.tests[id].fold:
			self.toggle_fold(id)

		k = tester.test_iter
		if tester.proc_run:
			k += 1
		iter = 0
		for i in range(k):
			if not tester.tests[i].fold:
				_beg_reg = v.get_regions(self.REGION_BEGIN_KEY % i)
				_end_reg = v.get_regions('test_end_%d' % i)

				v.erase_regions(self.REGION_BEGIN_KEY % i)
				v.erase_regions('test_end_%d' % i)

				v.add_regions(self.REGION_BEGIN_KEY % iter, \
				_beg_reg, *self.REGION_BEGIN_PROP)

				v.add_regions('test_end_%d' % iter, \
					_end_reg, *self.REGION_END_PROP)

			if i != id:
				iter += 1

		del tester.tests[id]
		del tester.prog_out[id]
		tester.test_iter -= 1
		self.memorize_tests()
		self.update_configs()

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
				# v.replace(edit, v.word(rs_beg.begin() + 5), str(cur_nth + 1))
				v.erase_regions(begin_key)
				v.add_regions(self.REGION_BEGIN_KEY % (cur_nth), [rs_beg], \
					*self.REGION_BEGIN_PROP)

				rs_line = v.get_regions('line_%d' % cur_nth)

				v.erase_regions('line_%d' % i)
				v.add_regions('line_%d' % cur_nth, rs_line, \
					*self.REGION_LINE_PROP)


				end_key = self.REGION_END_KEY % i
				rs_end = v.get_regions(end_key)
				if rs_end:
					rs_end = rs_end[0]
					v.erase_regions(end_key)
					v.add_regions(self.REGION_END_KEY % (cur_nth), [rs_end], \
						*self.REGION_END_PROP)

				cur_nth += 1

	def delete_tests(self, edit):
		v = self.view
		tester = self.tester

		if tester.proc_run:
			sublime.status_message('stop process before delete action')
			return

		if tester.proc_run:
			k = tester.test_iter + 1
		else:
			k = tester.test_iter
			
		to_del = []
		for i in range(k):
			begin = self.get_tie_pos(i)
			if i == k - 1:
				end = v.size()
			else:
				end = self.get_tie_pos(i + 1)
			r = Region(begin, end)
			for sel in v.sel():
				if sel.intersects(r):
					to_del.append(i)

		sublime.status_message('deleted tests: ' + (', '.join(map(lambda x: str(x + 1), to_del))))
		for test in reversed(to_del):
			self.delete_test(edit, test)
		self.memorize_tests()

	def sync_read_only(self):
		view = self.view
		tester = self.tester

		err = True
		if tester and tester.proc_run:
			err = False
			forb_before = self.delta_input
			forb_after = view.line(self.delta_input).b
			forbs = [Region(0, forb_before)]
			forbs.append(Region(forb_after, view.size() - 1))

			for forb in forbs:
				for sel in view.sel():
					if forb.intersects(sel):
						err = True

			delete_forb = False
			for sel in view.sel():
				if sel.a == self.delta_input or sel.begin() == 0:
					delete_forb = True
					break

			view.settings().set('delete_forb', delete_forb)

		view.set_read_only(err)

	def enable_edit_mode(self):
		v = self.view
		if self.tester.proc_run:
			self.tester.terminate()
			# sublime.set_timeout_async(self.enable_edit_mode, 500)
			sublime.set_timeout_async(lambda :v.run_command('test_manager', {'action': 'enable_edit_mode'}), 500)
			return

		if v.settings().get('edit_mode'): return
		v.settings().set('edit_mode', True)

		tests = self.tester.test_iter
		for i in range(tests):
			out_begin = v.get_regions(self.REGION_END_KEY % i)[0].begin()
			if i == tests - 1:
				out_end = v.size()
			else:
				out_end = v.get_regions(self.REGION_BEGIN_KEY % (i + 1))[0].begin()
			v.erase_regions(self.REGION_END_KEY % i)
			v.erase_regions('line_%d' % i)
			v.erase_regions('test_error_%d' % i)
			v.run_command('test_manager', {
				'action': 'erase',
				'region': (out_begin, out_end)
			})
		self.sync_read_only()

	def get_begin_region(self, id):
		v = self.view
		return v.get_regions(self.REGION_BEGIN_KEY % id)

	def apply_edit_changes(self):
		v = self.view

		tests = []
		i = 0
		while self.get_begin_region(i):
			st = self.get_begin_region(i)[0].begin()
			if not self.get_begin_region(i + 1):
				end = v.size()
			else:
				end = self.get_begin_region(i + 1)[0].begin()
			tests.append(v.substr(Region(st, end)).strip() + '\n')
			i += 1

		self.tester.set_tests(tests)
		self.memorize_tests()

	def toggle_new_test(self):
		v = self.view
		places = []
		i = 0
		while self.get_begin_region(i):
			places.append(self.get_begin_region(i)[0].begin())
			i += 1
		cur = v.line(v.sel()[0].begin()).begin()
		if cur in places:
			places.remove(cur)
			v.erase_regions(self.REGION_BEGIN_KEY % len(places))
		else:
			places.append(cur)
			places.sort()

		for i in range(len(places)):
			v.erase_regions(self.REGION_BEGIN_KEY % i)
			v.add_regions(self.REGION_BEGIN_KEY % i, [Region(places[i], places[i])], \
				*self.REGION_BEGIN_PROP)

	def swap_tests(self, edit, dir=-1):
		tester = self.tester
		view = self.view
		selected = []
		unfold = []

		for i in range(len(tester.tests)):
			begin = self.get_tie_pos(i)
			end = self.get_tie_pos(i + 1)

			tester.tests[i].__sel = []

			for reg in view.sel():
				if reg.intersects(Region(begin, end)):
					selected.append(i)
					inter = reg.intersection(Region(begin, end))
					tester.tests[i].__sel.append(Region(inter.a - begin, inter.b - begin))
					break

		for i in range(len(tester.tests)):
			if not tester.tests[i].fold:
				tester.tests[i].__unfold = True
				self.toggle_fold(i)
			else:
				tester.tests[i].__unfold = False

		if dir == 1:
			selected.reverse()
		for sel in selected:
			if 0 <= sel + dir < len(tester.tests):
				tester.tests[sel], tester.tests[sel + dir] = tester.tests[sel + dir], tester.tests[sel]
				tester.prog_out[sel], tester.prog_out[sel + dir] = tester.prog_out[sel + dir], tester.prog_out[sel]

		for i in range(len(tester.tests)):	
			if tester.tests[i].__unfold:
				self.toggle_fold(i)
		view.sel().clear()
		for i in range(len(tester.tests)):
			for x in tester.tests[i].__sel:
				begin = self.get_tie_pos(i)
				view.sel().add(Region(begin + x.a, begin + x.b))

	def toggle_hide_phantoms(self):
		view = self.view
		view.settings().set('hide_phantoms', not view.settings().get('hide_phantoms'))
		self.update_configs()

	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False, \
			sync_out=False, code_view_id=None, var_name=None, use_debugger=False, pos=None, \
			load_session=False, region=None, frame_id=None, data=None, id=None, dir=1):

		v = self.view

		v.set_read_only(False)

		if action == 'insert_line':
			self.insert_text(edit)

		elif action == 'insert_cb':
			self.insert_cb(edit)

		elif action == 'insert_opd_input':
			v.insert(edit, self.delta_input, text)
			self.delta_input += len(text)

		elif action == 'insert_opd_out':
			v.insert(edit, self.delta_input, text)
			self.delta_input += len(text)

		elif action == 'replace':
			v.replace(edit, Region(region[0], region[1]), text)

		elif action == 'erase':
			v.erase(edit, Region(region[0], region[1]))

		elif action == 'apply_edit_changes':
			self.apply_edit_changes()

		elif action == 'make_opd':
			self.make_opd(edit, run_file=run_file, build_sys=build_sys, clr_tests=clr_tests, \
				sync_out=sync_out, code_view_id=code_view_id, use_debugger=use_debugger, load_session=load_session)

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

		elif action == 'set_test_input':
			self.set_test_input(id=id, test=data)

		elif action == 'delete_test':
			self.delete_test(edit, id)

		elif action == 'swap_tests':
			self.swap_tests(edit, dir=dir)

		elif action == 'toggle_hide_phantoms':
			self.toggle_hide_phantoms()

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


class ModifiedListener(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		if view.get_status('opd_info') == 'opdebugger-file' and not view.settings().get('edit_mode'):
			view.run_command('test_manager', { 'action': 'sync_read_only' })

	def on_hover(self, view, point, hover_zone):
		if hover_zone == sublime.HOVER_TEXT:
			view.run_command('view_tester', { 'action': 'get_var_value', 'pos': point })

class CloseListener(sublime_plugin.EventListener):
	"""Listen to Close"""
	def __init__(self):
		super(CloseListener, self).__init__()

	def on_pre_close(self, view):
		if view.get_status('opd_info') == 'opdebugger-file':
			view.run_command('test_manager', {'action': 'close'})


class ViewTesterCommand(sublime_plugin.TextCommand):
	ROOT = dirname(__file__)
	ruler_opd_panel = 0.68
	have_tied_dbg = False
	use_debugger = False

	def create_opd(self, clr_tests=False, sync_out=True, use_debugger=False):
		'''
		creates opd with supported language
		'''
		v = self.view
		if v.is_dirty():
			v.run_command('save')
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		file_name = v.file_name()
		file_ext = path.splitext(file_name)[1][1:]

		window = v.window()
		v.erase_regions('crash_line')

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
			if get_settings().get('close_sidebar'):
				try:
					sublime.set_timeout_async(lambda window=window: window.set_sidebar_visible(False), 50)
				except:
					# Version of sublime text < 3102
					pass
			dbg_view.run_command('toggle_setting', {'setting': 'word_wrap'})

		if len(window.get_layout()['cols']) != 3 or window.get_layout()['cols'][1] >= 0.89:
			window.set_layout({
				'cols': [0, self.ruler_opd_panel, 1],
				'rows': [0, 1],
				'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
			})

		window.set_view_index(dbg_view, 1, 0)
		window.focus_view(v)
		window.focus_view(dbg_view)

		dbg_view.set_syntax_file('Packages/%s/TestSyntax.tmLanguage' % base_name)
		dbg_view.set_name(os.path.split(v.file_name())[-1] + ' -run')
		dbg_view.run_command('set_setting', {'setting': 'fold_buttons', 'value': False})
		dbg_view.run_command('test_manager', {
			'action': 'make_opd', 
			'build_sys': file_syntax, 
			'run_file': v.file_name(), 
			'clr_tests': clr_tests, 
			'sync_out': sync_out, 
			'code_view_id': v.id(), \
			'use_debugger': use_debugger
		})
	
	def close_opds(self):
		w = self.view.window()
		tied_id = None
		if self.have_tied_dbg:
			tied_id = self.tied_dbg.id()
		for v in w.views():
			if v.id() == tied_id: continue
			if v.name()[::-1][:len('-run')][::-1] == '-run':
				v.close()

	def get_var_value(self, pos=None):
		view = self.view
		if pos is None:
			pt = view.sel()[0].begin()
		else:
			pt = pos
		var_name = view.substr(view.word(pt))
		if self.have_tied_dbg:
			dbg = self.tied_dbg
			dbg.run_command('test_manager', {
				'action' : 'redirect_var_value',
				'var_name': var_name,
				'pos': pt
			})

	def show_frames(self, frames=None):
		v = self.view
		
		if not self.have_tied_dbg:
			sublime.status_message('nothing to show')
			return

		dbg_view = self.tied_dbg

		if not frames:
			dbg_view.run_command('test_manager', {
				'action': 'redirect_frames'
			})
			return

		def sep(desc):
			bal = 0
			for i in range(len(desc)):
				if desc[i] == '(':
					bal += 1
				elif desc[i] == ')':
					bal -= 1
					if bal == 0:
						return [desc[:i + 1], desc[i + 2:]]
			return desc

		frames = eval(frames)
		items = [sep(frame['desc']) for frame in frames]

		def on_select(id):
			v.erase_regions('highlight')
			if id == -1: return
			pt = v.text_point(int(frames[id]['line']) - 1, 0)
			v.show_at_center(pt)
			v.sel().clear()
			v.sel().add(v.line(pt))
			v.run_command('view_tester', {
				'action': 'show_crash_line',
				'crash_line': int(frames[id]['line'])
			})

			dbg_view.run_command('test_manager', {
				'action': 'select_frame',
				'frame_id': id		
			})

		def on_highlight(id, frames=frames):
			pt = v.text_point(int(frames[id]['line']) - 1, 0)
			v.show_at_center(pt)
			v.add_regions('highlight', [v.line(pt)], 'variable.c++', 'dot', sublime.HIDDEN)

		v.window().show_quick_panel(items, on_select, sublime.MONOSPACE_FONT, 0, on_highlight)

	def show_var_value(self, value, pos=None):
		def nop(): pass
		self.view.show_popup(highlight(value), sublime.HIDE_ON_MOUSE_MOVE_AWAY, pos)

	def toggle_using_debugger(self):
		self.use_debugger ^= 1
		if self.use_debugger:
			sublime.status_message('debugger enabled')
		else:
			sublime.status_message('debugger disabled')


	def run(self, edit, action=None, clr_tests=False, text=None, sync_out=True, \
			crash_line=None, value=None, pos=None, frames=None, use_debugger=False):
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		if action == 'insert':
			v.insert(edit, v.sel()[0].begin(), text)
		elif action == 'make_opd':
			if v.settings().get('syntax') == 'Packages/FastOlympicCoding/OPDebugger.tmLanguage':
				v.run_command('test_manager', {
					'action': 'make_opd',
					'load_session': True,
					'use_debugger': use_debugger
				})
			else:
				self.close_opds()
				self.create_opd(clr_tests=clr_tests, sync_out=sync_out, use_debugger=use_debugger)
		elif action == 'show_crash_line':
			pt = v.text_point(crash_line - 1, 0)
			v.erase_regions('crash_line')
			v.add_regions('crash_line', [sublime.Region(pt + 0, pt + 0)], \
				'variable.language.python', 'Packages/FastOlympicCoding/icons/arrow_right.png', \
				sublime.DRAW_SOLID_UNDERLINE)
			sublime.set_timeout_async(lambda pt=pt: v.show_at_center(pt), 39)

		elif action == 'get_var_value':
			self.get_var_value(pos=pos)

		elif action == 'show_var_value':
			self.show_var_value(value, pos=pos)

		elif action == 'show_frames':
			self.show_frames(frames=frames)

		elif action == 'toggle_using_debugger':
			self.toggle_using_debugger()

		elif action == 'sync_opdebugs':
			w = v.window()
			layout = w.get_layout()

			if len(layout['cols']) == 3:
				if layout['cols'][1] != 1:
					# hide opd panel
					self.ruler_opd_panel = min(layout['cols'][1], 0.93)
					layout['cols'][1] = 1
					w.set_layout(layout)
				else:
					# show opd panel
					layout['cols'][1] = self.ruler_opd_panel
					need_x = self.ruler_opd_panel
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
			# print(view.name())
			if view.name()[-4:] == '-run':
				w.set_view_index(view, 1, 0)
				# print('moved to second group')
			elif prop[0] == 1:
				active_view_index = w.get_view_index(w.active_view_in_group(0))[1]
				# print('moved to first group')
				w.set_view_index(view, 0, active_view_index + 1)
		except:
			pass
		

	# def on_load(self, view):
	# 	self.move_syncer(view)

	# def on_new(self, view):
	# 	self.move_syncer(view)