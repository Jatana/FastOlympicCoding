import sublime, sublime_plugin
import os
from os import path
from .ContestHandlers import codeforces
from .test_manager import TestManagerCommand

handlers = [codeforces]

class ContestHandlerCommand(sublime_plugin.TextCommand):
	def create_path(self, base, _path):
		for i in range(len(_path)):
			cur = path.join(base, path.join(*_path[:i + 1]))
			if not path.exists(cur):
				os.mkdir(cur)
		return path.join(base, path.join(*_path))

	def init_problems(self, handler, contest_id, base, pid=0):
		inputs, outputs = handler.try_load_tests(contest_id, pid)
		if inputs:
			file_name = path.join(base, chr(ord('A') + pid) + '.cpp')
			if not path.exists(file_name):
				file = open(file_name, 'w')
				file.close()
			tests = [] 
			for i in range(len(inputs)):
				tests.append({
					'test': inputs[i],
					'correct_answers': [outputs[i]]
				})
			file = open(file_name + TestManagerCommand.TESTS_FILE_SUFFIX, 'w')
			file.write(sublime.encode_value(tests, True))
			file.close()
			def go(self=self, handler=handler, contest_id=contest_id, base=base, pid=pid + 1):
				self.init_problems(handler, contest_id, base, pid=pid)
			sublime.set_timeout_async(go)

	def init_contest(self, handler, contest_id):
		base = self.create_path(path.expanduser('~'), ['contest_base', handler.get_basename(), handler.get_contest_info(contest_id)['title']])
		sublime.run_command('new_window')
		sublime.active_window().set_project_data({'folders': [{'path': base}]})
		self.init_problems(handler, contest_id, base)

	def try_init_contest(self, url, on_init):
		for handler in handlers:
			if handler.is_valid_url(url):
				self.init_contest(handler, handler.extract_contest_id(url))
				return

	def run(self, edit, action=None):
		if action == 'setup_contest':
			def on_done(url, self=self):
				self.try_init_contest(url, None)

			def on_change(url):
				pass

			def on_cancel():
				pass

			self.view.window().show_input_panel(
				'URL',
				'https://codeforces.com/contest/1056/problem/C',
				on_done,
				on_change,
				on_cancel
			)
