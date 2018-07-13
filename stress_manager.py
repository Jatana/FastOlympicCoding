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
		result = self.start_test()
		self.test_id += 1
		if not result['success']:
			if result['crash'] and not result['log']:
				sublime.message_dialog(result['message'])
			else:
				result_view = view.window().new_file()
				result_view.set_scratch(True)
				# result_view.run_command('set_setting', {'setting': 'fold_buttons', 'value': False})
				# result_view.run_command('set_setting', {'setting': 'line_numbers', 'value': False})
				# result_view.run_command('set_setting', {'setting': 'gutter', 'value': False})
				if result['crash']:
					text = 'test:\n{test}\noutput:\n{output}\nerror:\n{error}'.format(
						error=result['message'],
						test=result['input'],
						output=result['output']
					)
				else:
					text = 'test:\n{test}\ngood:\n{good}\nbad:\n{bad}'.format(
						test=result['test_data'],
						good=result['good_output'],
						bad=result['bad_output']
					)
				result_view.run_command('stress_manager', {
					'action': 'insert_result',
					'text': text 
				})
		else:
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
					'crash': True,
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
				'crash': True,
				'output': ''
			}

	def start_test(self):
		seed = str(randint(0, int(1e9)))
		tl = get_settings().get('stress_time_limit_seconds')

		data = self.perfom_run(self.gen_process, seed, tl)
		if not type(data) == str:
			data['log'] = False
			return data
		test_data = data

		data = self.perfom_run(self.good_process, test_data, tl)
		if not type(data) == str:
			data['log'] = True
			return data
		good_output = data

		data = self.perfom_run(self.bad_process, test_data, tl)
		if not type(data) == str:
			data['log'] = True
			return data
		bad_output = data

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
			resp['success'] = True
		return resp

	def run(self, edit, action=None, text=''):
		view = self.view
		window = view.window()
		if action == 'make_stress':
			file = view.file_name()
			ext = path.splitext(file)[1][1:]
			base_dir = path.dirname(file)
			task_name = path.splitext(path.split(file)[1])[0]
			bad_source = file
			good_source = path.join(base_dir, task_name + '__Good.cpp')
			gen_source = path.join(base_dir, task_name + '__Generator.cpp')
			def check_exist(source):
				if not path.exists(source):
					sublime.error_message(source + ' not found')
					return False
				return True
			
			if check_exist(good_source) and check_exist(bad_source) and check_exist(gen_source):
				self.good_process = ProcessManager(
					good_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.bad_process = ProcessManager(
					bad_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.gen_process = ProcessManager(
					gen_source,
					None,
					run_settings=get_settings().get('run_settings')
				)

				self.good_process.compile()
				self.bad_process.compile()
				self.gen_process.compile()
				self.test_id = 1
				self.stop_stress = False
				sublime.set_timeout_async(self.provide_stress, 100)
		elif action == 'stop_stress':
			self.stop_stress = True
		elif action == 'insert_result':
			view.insert(edit, 0, text)
