import sublime, sublime_plugin
import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
import shlex
from sublime import Region
from os import path


from FastOlympicCoding.Modules.ProcessManager import ProcessManager
from FastOlympicCoding.Modules import basics
from FastOlympicCoding.settings import root_dir, plugin_name, run_options
from FastOlympicCoding.Engine import SysManager


class DebuggerCommand(sublime_plugin.TextCommand):
	BEGIN_TEST_STRING = 'Test %d {'
	END_TEST_STRING = '} returncode %d'
	REGION_BEGIN_KEY = 'test_begin_%d'
	REGION_END_KEY = 'test_end_%d'
	REGION_POS_PROP = ['', '', sublime.HIDDEN]
	REGION_ACCEPT_PROP = ['string', 'dot', sublime.HIDDEN]
	REGION_DECLINE_PROP = ['variable.c++', 'dot', sublime.HIDDEN]
	REGION_UNKNOWN_PROP = ['text.plain', 'dot', sublime.HIDDEN]

	# Test
	#REGION_POS_PROP = REGION_UNKNOWN_PROP


	class Test(object):
		"""
		class for tests buffer
		continues data of start, end, correct and uncorrect answers
		"""
		def __init__(self, prop, start=None, end=None):
			super(DebuggerCommand.Test, self).__init__()
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
		def __init__(self, process_manager, on_insert, on_out, on_stop, sync_out=False, tests=[]):
			super(DebuggerCommand.Tester, self).__init__()
			self.process_manager = process_manager
			self.sync_out = sync_out
			self.tests = tests
			self.test_iter = 0
			self.on_insert = on_insert
			self.on_out = on_out
			self.on_stop = on_stop
			self.proc_run = False
			self.prog_out = []

		def __on_out(self, s):
			n = self.test_iter
			self.prog_out[n] += s
			self.on_out(s)

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
				'output already puted'
			self.proc_run = False
			self.test_iter += 1
			self.on_stop(proc.is_stopped())

		def insert(self, s, call_on_insert=False):
			n = self.test_iter
			if self.proc_run:
				# self.on_insert(s)
				self.tests[n].append_string(s)
				self.process_manager.insert(s)
				if call_on_insert:
					self.on_insert(s)

		def insert_test(self):
			n = self.test_iter
			tests = self.tests
			if n == 0:
				self.process_manager.compile()
			if n < len(tests):
				self.process_manager.run_file()
				self.proc_run = True
				self.process_manager.insert(tests[n].test_string)
				self.on_insert(tests[n].test_string)

		def next_test(self):
			n = self.test_iter
			tests = self.tests
			prog_out = self.prog_out
			if n >= len(tests):
				tests.append(DebuggerCommand.Test(''))
			if n >= len(prog_out):
				prog_out.append('')
			self.insert_test()
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

		def del_tests(self, to_del):
			dont_add = set(to_del)
			tests = self.tests
			new_tests = []
			for i in range(len(tests)):
				if not i in dont_add:
					new_tests.append(tests[i])

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
		self.tester.next_test()
		v.window().active_view().set_status('process_status', 'Process Run')
		if self.tester.test_iter > 4:
			self.fold_accept_tests()



	def memorize_tests(self):
		# print([x.memorize() for x in (self.tester.get_tests())])
		f = open(self.dbg_file + ':tests', 'w')
		f.write(sublime.encode_value([x.memorize() for x in (self.tester.get_tests())], True))
		f.close()

	def on_insert(self, s):
		self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': s})

	def on_out(self, s):
		self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': s})

	def on_stop(self, rtcode):
		v = self.view
		self.view.run_command('debugger', {'action': 'insert_opd_out', \
			'text': (('\n' + self.END_TEST_STRING + '\n') % rtcode)})
		v.add_regions("test_end_%d" % (self.tester.test_iter - 1), \
			[Region(v.line(v.size() - 2).begin(), v.line(v.size() - 2).begin() + 1)], \
				*self.REGION_POS_PROP)
		tester = self.tester
		self.view.erase_status('process_status')
		if tester.have_pretests():
			self.view.run_command('debugger', {'action': 'new_test'})
		else:
			self.memorize_tests()
		# print(self.tester.prog_out)
		cur_test = self.tester.test_iter - 1
		check = self.tester.check_test(cur_test)
		if check:
			self.set_test_status(cur_test, accept=True, call_tester=False)
		elif check is False:
			self.set_test_status(cur_test, accept=False, call_tester=False)

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
		else:
			prop = self.REGION_DECLINE_PROP
			if call_tester:
				self.tester.decline_out(nth)
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
				v.fold(Region(beg + 6, end))
				



	def make_opd(self, edit, run_file=None, build_sys=None, clr_tests=False, sync_out=False):
		v = self.view
		v.set_scratch(True)
		v.set_status('opd_info', 'opdebugger-file')
		v.run_command('debugger', {'action': 'erase_all'})
		self.dbg_file = run_file
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
		process_manager = ProcessManager(run_file, build_sys, run_options=run_options)
		cmp_data = process_manager.compile()
		if cmp_data is None or cmp_data[0] == 0:
			self.tester = self.Tester(process_manager, \
				self.on_insert, self.on_out, self.on_stop, tests=tests, sync_out=sync_out)
			v.run_command('debugger', {'action': 'new_test'})
			v.set_status('process_status', 'Process Run')
		else:
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': cmp_data[1]})

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
					*self.REGION_POS_PROP)


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
		print('deleted', to_del)
		for x in to_del:
			self.delete_nth_test(edit, x)
		self.tester.del_tests(to_del)
		self.renumerate_tests(edit, cur_test + 2)
		if self.tester.proc_run:
			self.delta_input = v.get_regions('delta_input')[0].begin()
		self.memorize_tests()

	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False, \
			sync_out=False):
		v = self.view
		pt = v.sel()[0].begin()
		scope_name = (v.scope_name(pt).rstrip())
		if action == 'insert_line':
			self.insert_text(edit)

		elif action == 'insert_cb':
			self.insert_cb(edit)

		elif action == 'insert_opd_out':
			v.insert(edit, self.delta_input, text)
			self.delta_input += len(text)

		elif action == 'make_opd':
			self.make_opd(edit, run_file=run_file, build_sys=build_sys, clr_tests=clr_tests, \
				sync_out=sync_out)

		elif action == 'close':
			try:
				self.process_manager.terminate()
			except:
				print('Error When terminating process')
			v.run_command('debugger', {'action': 'erase_all'})

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
			v.run_command('debugger', {'action':'erase_all'})

		elif action == 'kill_proc':
			self.tester.terminate()


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
			# view.run_command('debugger', {'action': 'sync_modified'})

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
			view.run_command('debugger', {'action': 'close'})
			print("specclose")
		# print('closed')

