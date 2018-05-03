import sublime, sublime_plugin
from os import path

from .settings import base_name, get_settings
from .Modules.ProcessManager import ProcessManager
from random import randint


class StressManagerCommand(sublime_plugin.TextCommand):
	def provide_stress(self):
		sublime.status_message('stressing, test: ' + str(self.test_id))
		result = self.start_test()
		self.test_id += 1
		if not result['success']:
			sublime.message_dialog('test:\n{test}\ngood:\n{good}\nbad:\n{bad}'.format(
				test=result['test_data'],
				good=result['good_output'],
				bad=result['bad_output']
			))
		else:
			if not self.stop_stress:
				sublime.set_timeout_async(self.provide_stress)
			else:
				sublime.status_message('stress stopped')

	def start_test(self):
		self.gen_process.run(args=[str(randint(0, int(1e9)))])
		test_data = self.gen_process.read() + '\n'
		self.good_process.run()
		self.good_process.write(test_data)
		self.bad_process.run()
		self.bad_process.write(test_data)
		good_output = self.good_process.read()
		bad_output = self.bad_process.read()
		resp = {
			'test_data': test_data,
			'good_output': good_output,
			'bad_output': bad_output,
		}
		if good_output.strip() != bad_output.strip():
			resp['success'] = False
		else:
			resp['success'] = True
		return resp

	def run(self, edit, action=None):
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




