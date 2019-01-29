import subprocess
from os import path
import sublime

BASE_DIR = path.dirname(path.abspath(__file__))
from .debugger_info import Debugger


def decode(data):
	# print('data:(', data)
	s = ''
	# print("data:", data)
	if not data:
		return ''
	data = eval(data.rstrip())
	for x in data:
		s += chr(x)
	return s

def encode(s):
	return str([ord(c) for c in s])
	return s


class PyLLDBDebugger(Debugger):
	"""docstring for PyLLDBDebugger"""
	supported_exts = ['cpp']
	RUN_PRIOR = 1


	def __init__(self, file):
		self.file = file
		self.last_state = ''
		self.selected_frame_id = None
		PIPE = subprocess.PIPE
		# subprocess.STDOUT
		self.proc_dbg = subprocess.Popen('python debugod.py "{name}"'.format(name=file), \
			shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, \
				cwd=BASE_DIR)
		# print(dir(self.proc_dbg.stdout))

	def is_runnable():
		return (sublime.platform() == 'osx')

	def has_var_view_api(self):
		return True

	def interact(self, action):
		# print('interaction: ', action)
		proc_dbg = self.proc_dbg
		proc_dbg.stdin.write((action + '\n').encode())
		proc_dbg.stdin.flush()
		return decode(proc_dbg.stdout.readline())

	def __listen(self):
		s = self.read()
		if s:
			self.cb_on_out(s)
		if self.is_running():
			sublime.set_timeout_async(self.__listen, 200)
		else:
			crash_line = None
			if self.is_stopped():
				crash_line = self.get_crash_line()
				if crash_line is not None:
					crash_line = int(crash_line)
			self.cb_on_stop(self.get_return_value(), runtime=self.get_runtime(), crash_line=crash_line)

	def __status_change_listener(self):
		state = self.get_state()
		if state != self.last_state:
			self.last_state = self.last_state
			self.cb_on_status_change(state)
		if not state in {'STOPPED', 'EXITED'}:
			sublime.set_timeout_async(self.__status_change_listener, 300)

	def set_calls(self, on_out, on_stop, on_status_change):
		self.cb_on_out = on_out
		self.cb_on_stop = on_stop
		self.cb_on_status_change = on_status_change

	def is_running(self):
		# print(self.interact('_.state'))
		return self.interact('_.state') == 'RUNNING'

	def is_exited(self):
		return self.interact('_.state') == 'EXITED'

	def is_stopped(self):
		return self.interact('_.state') == 'STOPPED'

	def get_state(self):
		return self.interact('_.state')

	def get_crash_line(self):
		return self.interact('_.crash_line')

	def get_return_value(self):
		return self.interact('_.rtcode')

	def get_runtime(self):
		return int(self.interact('_.get_runtime()'))

	def cut_var_value(self, value):
		try:
			bal = 1
			i = value.index('(') + 1
			while bal > 0:
				if value[i] == '(':
					bal += 1
				if value[i] == ')':
					bal -= 1
				i += 1
			return value[i + 1:]
		except:
			return value

	def get_var_value(self, var_name, frame_id=None):
		return self.cut_var_value(
			self.interact(
				'_.get_var_value(decode({bytes}.__str__()), frame_id={frame_id})'
					.format(bytes=encode(var_name), frame_id=self.selected_frame_id)
				)
			)

	def get_frames(self):
		return self.interact('_.get_frames()')

	def select_frame(self, id):
		self.selected_frame_id = id

	def get_compile_cmd(self):
		return self.interact('_.get_compile_cmd()')

	def compile(self):
		return eval(self.interact('_.compile()'))

	def run(self):
		self.interact('_.run()')
		self.__listen()
		self.__status_change_listener()

	def write(self, s):
		# print('_.put_stdin(decode({bytes}.__str__()))'.format(bytes=encode(s)))
		return self.interact('_.put_stdin(decode({bytes}.__str__()))'.format(bytes=encode(s)))

	def read(self):
		out = self.interact('_.get_output()')
		# print(out)
		return out

	def terminate(self):
		self.interact('_.terminate()')

	def quit(self):
		self.interact('quit()')
		exit(0)




# dbg = PyLLDBDebugger('')

# while True:
	# print(eval(input()))

# print(dbg.interact('_.compile()'))
# print(dbg.interact('_.run()'))
# for i in range(int(1e7)):
	# print(end='')
# print(dbg.interact('_.get_var_value(10, "v")'))
# print(dbg.interact('quit()'))
