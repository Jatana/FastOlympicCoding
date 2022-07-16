import sublime, sublime_plugin
import os
from os import path
from .ContestHandlers import codeforces
try:
	from .ContestHandlers.codeforces_submit import perform_submission
except ImportError:
	pass
from .test_manager import TestManagerCommand
from sublime import Region
from .settings import get_tests_file_path, get_settings

handlers = [codeforces]


class ContestHandlerCommand(sublime_plugin.TextCommand):
	def create_path(self, base, _path):
		for i in range(len(_path)):
			cur = path.join(base, path.join(*_path[:i + 1]))
			if not path.exists(cur):
				os.mkdir(cur)
		return path.join(base, path.join(*_path))

	def next_problem(self, pid):
		if len(pid) == 1: return chr(ord(pid[0]) + 1)
		return pid[0] + chr(ord(pid[1]) + 1)

	def init_problems(self, handler, contest_id, base, pid='A'):
		inputs, outputs = handler.try_load_tests(contest_id, pid)
		if inputs:
			file_name = path.join(base, pid + '.cpp')
			if not path.exists(file_name):
				file = open(file_name, 'w')
				file.close()
			tests = [] 
			for i in range(len(inputs)):
				tests.append({
					'test': inputs[i],
					'correct_answers': [outputs[i]]
				})

			with open(get_tests_file_path(file_name), 'w') as f:
				f.write(sublime.encode_value(tests, True))

			def go(self=self, handler=handler, contest_id=contest_id, base=base, pid=self.next_problem(pid)):
				self.init_problems(handler, contest_id, base, pid=pid)

			sublime.set_timeout_async(go)
		else:
			if len(pid) == 1:
				self.init_problems(handler, contest_id, base, pid + '1')
			elif pid[1] == '1':
				sublime.status_message('tests loaded')
				return
			else:
				self.init_problems(handler, contest_id, base, chr(ord(pid[0]) + 1))

	def init_contest(self, handler, contest_id):
		base = self.create_path(path.expanduser('~'), ['contest_base', handler.get_basename(), handler.get_contest_info(contest_id)['title']])
		sublime.run_command('new_window')
		sublime.active_window().set_project_data({'folders': [{'path': base}]})
		fsettings = path.join(base, '_contest.sublime-settings')
		if not path.exists(fsettings):
			settings = {
				'contestID': contest_id
			}
			open(fsettings, 'w').write(sublime.encode_value(settings, True))

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
		elif action == 'submit':
			for folder in self.view.window().folders():
				file = path.join(folder, '_contest.sublime-settings')
				if path.exists(file):
					settings = sublime.decode_value(open(file).read())
					break
			else:
				print('_contest.sublime-settings is not found')
				return
			code = self.view.substr(Region(0, int(1e9)))
			last = path.basename(self.view.file_name())
			problemID = path.splitext(last)[0]
			print('args', settings, problemID)
			def reduce(
					settings=settings,
					problemID=problemID,
					code=code,
					username=get_settings().get('cf_username'),
					password=get_settings().get('cf_password')):
				perform_submission(settings['contestID'], problemID, code, {
						'username': username, 'password': password
					}
				)
			sublime.set_timeout_async(reduce, 10)
