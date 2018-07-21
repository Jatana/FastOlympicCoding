import sublime, sublime_plugin
from os import path

from .settings import base_name, get_settings
from .Modules.ProcessManager import ProcessManager
from random import randint
from subprocess import TimeoutExpired


class StressManagerCommand(sublime_plugin.TextCommand):
	def provide_stress(self):
		view = self.view
		sublime.status_message('stressing, test: ' + str(self.test_id))
		view.set_name('Stress: Test #' + str(self.test_id))
		result = self.start_test()
		self.test_id += 1
		if result['success']:
			if not self.stop_stress:
				sublime.set_timeout_async(self.provide_stress)
			else:
				sublime.status_message('stress stopped')

	def perfom_run(self, process, input, tl):
		process.run()
		try:
			outs, errs = process.communicate(input, timeout=tl)
			if process.is_stopped() != 0:
				return {
					'success': False,
					'input': input,
					'message': process.file + ': crashed with exit code: %d' % process.is_stopped(),
					'output': outs
				}
			else:
				return outs 
		except TimeoutExpired:
			process.terminate()
			return {
				'success': False,
				'input': input,
				'message': process.file + ': time limit exceeded (%d seconds)' % tl,
				'output': ''
			}

	def _print_log(self, test_data, good_output, bad_output):
		view = self.view
		text = 'test #{test_id}:\n{test_data}\ngood:\n{good_output}\nbad:\n{bad_output}'
		text = text.format(
			test_id=self.test_id,
			test_data=self.shift_right(test_data),
			good_output=self.shift_right(good_output),
			bad_output=self.shift_right(bad_output)
		)
		view.run_command('stress_manager', {
			'action': 'insert_result',
			'text': text 
		})

	def start_test(self):
		seed = str(randint(0, int(1e9)))
		tl = get_settings().get('stress_time_limit_seconds')

		data = self.perfom_run(self.process['gen'], seed, tl)
		if not type(data) == str:
			self._print_log(data['message'], '', '')
			return data

		test_data = data
		self._print_log(test_data, '', '')
		err = False	
		data = self.perfom_run(self.process['good'], test_data, tl)
		if not type(data) == str:
			good_output = data['message']
			err = True
		else:
			good_output = data
		self._print_log(test_data, good_output, '')

		data = self.perfom_run(self.process['bad'], test_data, tl)
		if not type(data) == str:
			bad_output = data['message']
			err = True
		else:
			bad_output = data

		self._print_log(test_data, good_output, bad_output)

		resp = {
			'test_data': test_data,
			'good_output': good_output,
			'bad_output': bad_output,
			'log': True,
			'crash': False
		}
		if good_output.strip() != bad_output.strip():
			resp['success'] = False
		else:
			resp['success'] = not err
		return resp

	def shift_right(self, s):
		return '\t' + s.replace('\n', '\n\t')

	def _print_compile_results(self, results):
		process = self.process
		view = self.view
		text = '{gen_file}:\n{gen_compile}\n{bad_file}:\n{bad_compile}\n{good_file}:\n{good_compile}'
		text = ''
		for key in process:
			text += process[key].file + ':' + '\n' + self.shift_right(results[key]) + '\n'
		
		view.run_command('stress_manager', {
			'action': 'insert_result',
			'text': text
		})

	def _compile(self):
		results = {
			'gen': 'compiling',
			'good': 'compiling',
			'bad': 'compiling',
		} 
		self._print_compile_results(results)
		ce = False
		for key in self.process:
			p = self.process[key]
			_result = p.compile()
			if _result is None:
				code, s = 0, ''
			else:
				code, s = _result[0], _result[1]

			if code: ce = True	
			results[key] = s if s else 'compiled'
			self._print_compile_results(results)

		if not ce:
			self.test_id = 1
			sublime.set_timeout_async(self.provide_stress, 100)

	def run(self, edit, action=None, text='', file=None):
		view = self.view
		window = view.window()
		if action == 'make_stress':
			file = view.file_name()
			stress_view = window.new_file()
			stress_view.run_command('stress_manager', {
				'action': 'init',
				'file': view.file_name()
			})

		elif action == 'init':
			view.set_name('Stress: Compile')
			view.set_syntax_file('Packages/%s/StressSyntax.tmLanguage' % base_name)
			view.set_scratch(True)
			view.run_command('set_setting', {'setting': 'line_numbers', 'value': False})
			ext = path.splitext(file)[1][1:]
			base_dir = path.dirname(file)
			task_name = path.splitext(path.split(file)[1])[0]

			def find_source(base_dir, name, run_settings):
				_found = None
				for lang in run_settings:
					for ext in lang['extensions']:
						src = path.join(base_dir, name + '.' + ext)
						if path.exists(src):
							if _found:
								return [_found, src]
							_found = src	
				return _found

			bad_source = file
			good_source = find_source(base_dir, task_name + '__Good', get_settings().get('run_settings'))
			gen_source = find_source(base_dir, task_name + '__Generator', get_settings().get('run_settings'))

			if not good_source:
				sublime.error_message(task_name + '__Good' + ' not found')
				return

			if not gen_source:
				sublime.error_message(task_name + '__Generator' + ' not found')
				return

			if type(good_source) is list:
				sublime.error_message('conflict files: ' + ' and '.join(good_source))
				return

			if type(gen_source) is list:
				sublime.error_message('conflict files: ' + ' and '.join(gen_source))
				return

			def check_exist(source):
				if not path.exists(source):
					sublime.error_message(source + ' not found')
					return False
				return True
			
			if check_exist(good_source) and check_exist(bad_source) and check_exist(gen_source):
				self.process = dict()
				self.process['good'] = ProcessManager(
					good_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.process['bad'] = ProcessManager(
					bad_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.process['gen'] = ProcessManager(
					gen_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.stop_stress = False
				sublime.set_timeout_async(self._compile)

		elif action == 'provide_stress':
			self.provide_stress()
				
		elif action == 'stop_stress':
			self.stop_stress = True
		elif action == 'insert_result':
			view.replace(edit, sublime.Region(0, view.size()), text)
			view.sel().clear()

class StressListener(sublime_plugin.EventListener):
	"""docstring for StressListener"""

	def on_close(self, view):
		if view.settings().get('syntax').find('StressSyntax') != -1:
			view.run_command('stress_manager', {
				'action': 'stop_stress'
			})
		
		