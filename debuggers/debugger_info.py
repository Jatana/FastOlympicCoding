import sublime

class Debugger(object):
	"""
	Debugger
	class for basics funcs of debugger
	"""

	# write what langs supported
	# sample cpp, py, pas, ...
	supported_exts = []

	def is_pro_debug(self):
		return True

	def __init__(self, file):
		'''
		make debug with `file`
		'''

	def is_runnable():
		'''
		check for can run on this computer
		'''
		return True

	def compile(self):
		'''
		compile if need file
		return None if compile ok
		return string if compile failed
		'''
		return None

	def run(self, args):
		'''
		run program with args
		args is string
		'''

	def set_calls(on_out, on_stop):
		'''
		please set calls
		and calls on program out or stop
		sample 
			on_out(s, is_err=False)
			on_stop(rtcode)
			on_crash(crash_line, rtcode)
		'''

	def write(self, s):
		'''
		write string to program
		'''

	def terminate(self):
		'''
		force terminating program
		'''


def get_debug_modules():
	return Debugger.__subclasses__()


from . import Cpp_OSX_Debugger
