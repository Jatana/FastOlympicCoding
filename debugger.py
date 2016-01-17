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

	def get_run_cmd(self, name, build_sys):
		if build_sys == 'source.c++':
			subprocess.check_call(['g++', name])
			return './a.out'
		elif build_sys == 'source.python':
			# return ['/bin/sh', 'python3', name]
			return '"/Library/Frameworks/Python.framework/Versions/3.4/bin/python3" ' + '"' + name + '"'

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
				f.write(sublime.encode_value(self.tests + self.cur_tests, True))
				f.close()
				self.cur_tests.append('')
			self.view.window().active_view().erase_status('process_status')
		else:
			sublime.set_timeout(self.on_stop, 100)


	def insert_pretests(self):
		n = self.ntest
		tests = self.tests
		if n < len(tests):
			self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': tests[n]})
			self.ntest += 1
			self.process_manager.insert(tests[n])

	def insert_text(self, edit, text=None):
		v = self.view
		if text is None:
			to_shove = (v.substr(v.full_line(v.sel()[0])))
			v.insert(edit, v.sel()[0].begin(), '\n')
		else:
			to_shove = text
			v.insert(edit, v.size(), to_shove + '\n')
		self.process_manager.insert(to_shove + '\n')
		self.cur_tests[-1] += to_shove + '\n'

	def run(self, edit, action=None, run_file=None, build_sys=None, text=None, clr_tests=False):
		v = self.view
		pt = v.sel()[0].begin()
		scope_name = (v.scope_name(pt).rstrip())
		if action == 'insert_line':
			self.insert_text(edit)
		elif action == 'insert_cb':
			to_shove = sublime.get_clipboard()
			w = ''
			for x in to_shove:
				if x == '\n':
					self.insert_text(edit, text=w)
					w = ''
				else:
					w += x
			v.insert(edit, v.size(), w)
					
		elif action == 'insert_opd_out':
			v.insert(edit, v.size(), text)
		elif action == 'make_opd':
			v.set_scratch(True)
			v.set_status('opd_info', 'opdebugger-file')
			v.run_command('debugger', {'action': 'erase_all'})
			if not v.settings().get('word_wrap'):
				v.run_command('toggle_setting', {"setting": "word_wrap"})
			if not clr_tests:
				try:
					f = open(run_file + ':tests')
					self.tests = sublime.decode_value(f.read())
					f.close()
				except:
					self.tests = []
			else:
				f = open(run_file + ':tests', 'w')
				f.write('[]')
				f.close()
				self.tests = []
			self.ntest = 0
			self.process_manager = ProcessManager(run_file, build_sys, run_options=run_options)
			self.cur_tests = ['']
			cmp_data = self.process_manager.compile()
			if cmp_data is None or cmp_data[0] == 0:
				v.insert(edit, 0, (self.BEGIN_TEST_STRING + '\n') % 1)
				self.process_manager.run_file()
				self.insert_pretests()
				v.window().active_view().set_status('process_status', 'Process Run')
				sublime.set_timeout(self.on_stop, 100)
			else:
				self.view.run_command('debugger', {'action': 'insert_opd_out', 'text': cmp_data[1]})
		elif action == 'close':
			try:
				self.process_manager.terminate()
			except:
				print('Error When terminating process')
			v.run_command('debugger', {'action': 'erase_all'})


		elif action == 'new_test':
			v.insert(edit, self.view.size(), \
				('\n' + self.BEGIN_TEST_STRING + '\n') % (self.process_manager.test_counter + 2))
			self.process_manager.new_test()
			self.insert_pretests()
			v.window().active_view().set_status('process_status', 'Process Run')
			sublime.set_timeout(self.on_stop, 100)
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
			self.process_manager.terminate()


	def isEnabled(view, args):
		print(view)




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

