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

from .Modules.ProcessManager import ProcessManager
from .settings import base_name, get_settings
from .debuggers import debugger_info
from .Highlight.CppVarHighlight import highlight


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
					s = proc.read(bfsize=1)
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
			# if n == 0:
				# self.process_manager.compile()
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

	def new_test(self, edit):
		v = self.view

		self.input_start = v.size()
		self.delta_input = v.size()
		self.output_start = v.size() + 1
		self.out_region_set = False
		
		# v.insert(edit, self.view.size(), '\n')
		# v.sel().clear()
		# v.sel().add(Region(v.size() - 1, v.size() - 1))

		v.add_regions('type', \
			[sublime.Region(v.size(), v.size())], *self.REGION_BEGIN_PROP)

		self.tester.next_test()

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
			# v.add_regions(self.REGION_OUT_KEY % (self.tester.test_iter + 1), \
				# [sublime.Region(v.size() - 1, v.size() - 1)], *self.REGION_OUT_PROP)
			self.out_region_set = True

	def add_region(self, line, region_prop):
		v = self.view
		pos = v.line(line)
		from random import randint
		v.add_regions(str(randint(0, 1e9)), [Region(pos.a, pos.a + 1)], *region_prop)


	def on_stop(self, rtcode, crash_line=None):
		v = self.view

		test_id = self.tester.test_iter - 1
		_inp = self.tester.tests[test_id].test_string
		_outp = self.tester.prog_out[test_id]

		v.run_command('test_manager', {
			'action': 'replace',
			'region': (self.input_start, v.size()),
			'text': _inp + '\n' + _outp 
		})

		v.erase_regions('type')


		line = v.line(self.input_start)

		v.add_regions(self.REGION_BEGIN_KEY % test_id, \
			[Region(line.begin(), line.end())], *self.REGION_BEGIN_PROP)

		v.add_regions('line_%d' % test_id, \
			[Region(line.begin(), line.end())], *self.REGION_LINE_PROP)

		if v.substr(v.size() - 1) != '\n' or not _outp:
			v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n'})

		rtcode = str(rtcode)
		if rtcode != '0':
			v.run_command('test_manager', {
				'action': 'insert_opd_out',
				'text': '<return {rtcode}>'.format(rtcode=rtcode)
			})
			v.add_regions('test_error_%d' % (test_id), \
				[Region(v.size() - 5, v.size() - 4)], 'variable.c++', 'dot', sublime.HIDDEN)
			v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n'})


		v.run_command('test_manager', {'action': 'insert_opd_out', 'text': '\n'})

		v.add_regions("test_end_%d" % test_id, \
			[Region(self.input_start + len(_inp) + 1, self.input_start + len(_inp) + 1)], \
				*self.REGION_END_PROP)

		v.run_command('test_manager', {'action': 'set_cursor_to_end'})

		tester = self.tester
		if str(rtcode) == '0':
			if tester.have_pretests():
				self.view.run_command('test_manager', {'action': 'new_test'})
			else:
				self.memorize_tests()

		cur_test = self.tester.test_iter - 1
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
		# print('VarName:', var_name, pos)
		if self.tester.process_manager.has_var_view_api():
			value = self.tester.process_manager.get_var_value(var_name)
			# print(value)
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

		# prop = self.get_style_test_status(nth)
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
		# name = self.view.name()
		# self.view.set_name(name[:name.index(' ')] + ' -' + status.lower())
		self.view.set_status('process_status', status)

	def clear_all(self):
		v = self.view
		v.run_command('test_manager', {'action': 'erase_all'})
		if self.tester:
			for i in range(self.tester.test_iter):
				v.erase_regions(self.REGION_BEGIN_KEY % i)
				v.erase_regions(self.REGION_END_KEY % i)
				v.erase_regions('line_%d' % i)
				v.erase_regions('test_error_%d' % i)

	def make_opd(self, edit, run_file=None, build_sys=None, clr_tests=False, \
		sync_out=False, code_view_id=None, use_debugger=False, load_session=False):
		self.use_debugger = use_debugger
		v = self.view

		self.delta_input = 0
		self.session = None

		if v.settings().get('edit_mode'):
			self.apply_edit_changes()

		v.set_scratch(True)
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

		if not v.settings().get('word_wrap'):
			v.run_command('toggle_setting', {"setting": "word_wrap"})

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
		DebugModule = debugger_info.get_best_debug_module(file_ext)
		if (not self.use_debugger) or (DebugModule is None):
			process_manager = ProcessManager(
				run_file,
				build_sys,
				run_settings=get_settings().get('run_settings')
			)
		else:
			process_manager = DebugModule(run_file)
		sublime.set_timeout_async(lambda :self.change_process_status('COMPILING'))
		cmp_data = process_manager.compile()
		if cmp_data is None or cmp_data[0] == 0:
			self.tester = self.Tester(process_manager, \
				self.on_insert, self.on_out, self.on_stop, self.change_process_status, \
				tests=tests, sync_out=sync_out)
			v.settings().set('edit_mode', False)
			v.run_command('test_manager', {'action': 'new_test'})
		else:
			v.run_command('test_manager', {'action': 'insert_opd_out', 'text': cmp_data[1]})

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

		view.set_read_only(have_sel_no_end or end_cursor)

	def enable_edit_mode(self):
		v = self.view 
		if v.settings().get('edit_mode'): return
		v.settings().set('edit_mode', True)

		if self.tester.proc_run:
			self.tester.terminate()
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


	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False, \
			sync_out=False, code_view_id=None, var_name=None, use_debugger=False, pos=None, \
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

		elif action == 'enable_edit_mode':
			self.enable_edit_mode()

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
		if view.get_status('opd_info') == 'opdebugger-file':
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

	def create_opd(self, clr_tests=False, sync_out=True):
		'''
		creates opd with supported language
		'''
		v = self.view
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
			dbg_view.run_command('toggle_setting', {'setting': 'line_numbers'})
			# dbg_view.run_command('toggle_setting', {"setting": "gutter"})
			try:
				sublime.set_timeout_async(lambda window=window: window.set_sidebar_visible(False), 50)
			except:
				# Version of sublime text < 3102
				pass
			dbg_view.run_command('toggle_setting', {'setting': 'word_wrap'})

		window.set_layout({
			'cols': [0, self.ruler_opd_panel, 1],
			'rows': [0, 1],
			'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
		})
		window.set_view_index(dbg_view, 1, 0)
		window.focus_view(v)
		window.focus_view(dbg_view)
		# opd_view.run_command('erase_view')
		dbg_view.set_syntax_file('Packages/%s/OPDebugger.tmLanguage' % base_name)
		dbg_view.set_name(os.path.split(v.file_name())[-1] + ' -run')
		dbg_view.run_command('set_setting', {'setting': 'fold_buttons', 'value': False})
		dbg_view.run_command('test_manager', {
			'action': 'make_opd', 
			'build_sys': file_syntax, 
			'run_file': v.file_name(), 
			'clr_tests': clr_tests, 
			'sync_out': sync_out, 
			'code_view_id': v.id(), \
			'use_debugger': self.use_debugger
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
		# print(value)
		def nop(): pass
		self.view.show_popup(highlight(value), sublime.HIDE_ON_MOUSE_MOVE_AWAY, pos)

	def toggle_using_debugger(self):
		self.use_debugger ^= 1
		if self.use_debugger:
			sublime.status_message('debugger enabled')
		else:
			sublime.status_message('debugger disabled')


	def run(self, edit, action=None, clr_tests=False, text=None, sync_out=True, \
			crash_line=None, value=None, pos=None, frames=None):
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
				'variable.language.python', 'Packages/FastOlympicCoding/icons/arrow_right.png', \
				sublime.DRAW_SOLID_UNDERLINE)
			sublime.set_timeout_async(lambda pt=pt: v.show_at_center(pt), 39)
			# print(pt)
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
		

	def on_load(self, view):
		self.move_syncer(view)

	def on_new(self, view):
		self.move_syncer(view)