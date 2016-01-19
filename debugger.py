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


class DebuggerCommand(sublime_plugin.TextCommand):
	BEGIN_TEST_STRING = 'Test %d {'
	END_TEST_STRING = '} returncode %d'

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
				self.correct_answers = prop.get('correct_answers', set())
				self.uncorrect_answers = prop.get('uncorrect_answers', set())

			self.start = start
			self.end = end

		def add_correct_answer(self, answer):
			self.correct_answers.add(answer.lstrip().rstrip())

		def add_uncorrect_answer(self, answer):
			self.uncorrect_answers.add(answer.lstrip().rstrip())

		def is_correct_answer(self, answer):
			if answer in correct_answers:
				return True
			if answer in uncorrect_answers:
				return False
			return None

		def append_string(self, s):
			self.test_string += s


		def set_inner_range(self, start, end):
			self.start = start
			self.end = end

		def memorize(self):
			return {
				"test": self.test_string,
				"correct_answers": list(self.correct_answers),
				"uncorrect_answers": list(self.uncorrect_answers)
			}

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
				self.on_out(s)
			try:
				s = proc.read()
				self.on_out(s)
			except:
				'output already puted'
			self.proc_run = False
			self.test_iter += 1
			self.on_stop(proc.is_stopped())

		def insert(self, s):
			n = self.test_iter
			if self.proc_run:
				# self.on_insert(s)
				self.tests[n].append_string(s)
				self.process_manager.insert(s)

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
			if n >= len(tests):
				tests.append(DebuggerCommand.Test(''))
			self.insert_test()
			sublime.set_timeout_async(self.__process_listener)

		def have_pretests(self):
			n = self.test_iter
			tests = self.tests
			return n < len(tests)

		def get_tests(self):
			return self.tests

		def terminate(self):
			self.process_manager.terminate()

	def on_stop(self):
		if self.process_manager.is_stopped() is not None:
			s = self.process_manager.get_output()
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': s})
			text = ('\n' + self.END_TEST_STRING) % self.process_manager.process.returncode
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': text})
			if self.ntest < len(self.tests):
				self.view.run_command('debugger', {'action': 'new_test'})
			if self.cur_tests[-1]:
				f = open(self.process_manager.file + ':tests', 'w')
				f.write(sublime.encode_value([x.memorize() for x in (self.tests + self.cur_tests)], True))
				f.close()
				self.cur_tests.append(self.Test(''))
			self.view.window().active_view().erase_status('process_status')
		else:
			sublime.set_timeout(self.on_stop, 100)


	def insert_pretests(self):
		n = self.ntest
		tests = self.tests
		if n < len(tests):
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': tests[n].test_string})
			self.ntest += 1
			self.process_manager.insert(tests[n].test_string)

	def insert_text(self, edit, text=None):
		v = self.view
		if text is None:
			if not self.tester.proc_run:
				return None
			to_shove = (v.substr(v.full_line(v.sel()[0])))
			v.insert(edit, v.sel()[0].begin(), '\n')
		else:
			to_shove = text
			v.insert(edit, v.size(), to_shove + '\n')
		self.tester.insert(to_shove + '\n')

	def insert_cb(self, edit):
		v = self.view
		to_shove = sublime.get_clipboard()
		w = ''
		for x in to_shove:
			if x == '\n':
				self.insert_text(edit, text=w)
				w = ''
			else:
				w += x
		v.insert(edit, v.size(), w)

	def new_test(self, edit):
		v = self.view
		# v.add_regions("test_begin_%d" % self.ntest, [Region(v.size(), v.size() + 1)], \
		# 	'string', 'dot', sublime.DRAW_SOLID_UNDERLINE)
		#print('kek')
		v.insert(edit, self.view.size(), \
				('\n' + self.BEGIN_TEST_STRING + '\n') % (self.tester.test_iter + 1))
		self.tester.next_test()
		v.window().active_view().set_status('process_status', 'Process Run')

	def on_insert(self, s):
		self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': s})

	def on_out(self, s):
		self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': s})

	def on_stop(self, rtcode):
		self.view.run_command('debugger', {'action': 'insert_opd_out', \
			'text': (self.END_TEST_STRING % rtcode)})
		tester = self.tester
		if tester.have_pretests():
			self.view.run_command('debugger', {'action': 'new_test'})
		else:
			f = open(self.dbg_file + ':tests', 'w')
			f.write(sublime.encode_value([x.memorize() for x in (self.tester.get_tests())], True))
			f.close()


	def make_opd(self, edit, run_file=None, build_sys=None, clr_tests=False, sync_out=False):
		v = self.view
		v.set_scratch(True)
		v.set_status('opd_info', 'opdebugger-file')
		v.run_command('debugger', {'action': 'erase_all'})
		self.dbg_file = run_file
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
		process_manager = ProcessManager(run_file, build_sys, run_options=run_options)
		cmp_data = process_manager.compile()
		if cmp_data is None or cmp_data[0] == 0:
			self.tester = self.Tester(process_manager, \
				self.on_insert, self.on_out, self.on_stop, tests=tests, sync_out=sync_out)
			self.tester.next_test()
			v.insert(edit, 0, (self.BEGIN_TEST_STRING + '\n') % 1)
			v.window().active_view().set_status('process_status', 'Process Run')
		else:
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': cmp_data[1]})

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
			v.insert(edit, v.size(), text)

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
			view.run_command('debugger', {'action': 'sync_modified'})



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

