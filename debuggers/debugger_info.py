import sublime

class Debugger(object):
	"""
	Debugger
	class for basics funcs of debugger
	"""

	# write what langs supported
	# sample cpp, py, pas, ...
	supported_exts = []
	RUN_PRIOR = 0.5

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

	def get_var_value(self, var_name, frame_id=None):
		'''
		returns var value
		if frame_id is None returns var `value at crashed frame
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
	print(Debugger.__subclasses__())
	print(sorted(Debugger.__subclasses__(), key=(lambda c: c.RUN_PRIOR), reverse=True))
	return sorted(Debugger.__subclasses__(), key=(lambda c: c.RUN_PRIOR), reverse=True)

def get_best_debug_module(ext):
	dbgs = []
	for dbg in Debugger.__subclasses__():
		if dbg.is_runnable():
			if ext in dbg.supported_exts:
				dbgs.append(dbg)
	dbgs.sort(key=lambda dbg: dbg.RUN_PRIOR)
	dbgs.reverse()
	if dbgs:
		return dbgs[0]
	return None



from . import Cpp_OSX_Debugger
# from . import DebugodPy3Ejector