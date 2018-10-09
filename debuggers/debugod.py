#!/usr/bin/python
import sys
import os
from os import path

base_dir = path.dirname(path.abspath(__file__))
framework = path.join(base_dir, 'LLDB.framework/Resources/Python')

sys.path.append(framework)

import lldb
from time import time
import subprocess
import threading


def encode(s):
	return str([ord(c) for c in s])
	return s

def decode(data):
	s = ''
	# print("data:", data)
	if not data:
		return ''
	data = eval(data.rstrip())
	for x in data:
		s += chr(x)
	return s

class Debugger(object):
	"""docstring for Debugger"""

	COMPILE_CMD = 'g++ -std=gnu++17 -g -o main "{name}"'


	def __init__(self, file):
		super(Debugger, self).__init__()
		self.file = file
		self.process = None
		self.main_thread = None
		self.sbdbg = None
		self.state = 'WAITING'
		self.debugger = None

	def change_state(self, new_state):
		self.state = new_state

	def clear(self):
		debugger = self.sbdbg
		if debugger:
			self.add_buff()
			self.process.Kill()
			lldb.SBDebugger.Destroy(self.sbdbg)

	def get_compile_cmd(self):
		return self.COMPILE_CMD.format(name=self.file)
		
	def compile(self):
		PIPE = subprocess.PIPE
		p = subprocess.Popen(self.COMPILE_CMD.format(name=self.file), \
			shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, \
				cwd=os.path.split(self.file)[0])
		self.change_state('COMPILING')
		p.wait()
		return (p.returncode, p.stdout.read().decode())

	def filter_frames(self):
		main_thread = self.main_thread
		frames = main_thread.frames
		cur_frames = []
		# print(self.file)
		for frame in frames:
			# print '!', type(frame.line_entry.file), '!'
			if frame.line_entry.file.__str__() == self.file:
				# print(frame.line_entry.file)
				cur_frames.append(frame)
		self.stack_frames = cur_frames

	def get_crash_frame(self):
		for frame in self.main_thread.frames:
			if frame.line_entry.file.__str__() == self.file:
				return frame

	class ExitListener(threading.Thread):
		def run(self):
			_ = self._dbg
			process = _.process
			broadcaster = process.GetBroadcaster()
			event = lldb.SBEvent()
			listener = lldb.SBListener('ExitListener')
			rc = broadcaster.AddListener(listener, lldb.SBProcess.eBroadcastBitStateChanged)
			while True:
				if listener.WaitForEventForBroadcasterWithType(lldb.eStateExited,
															   broadcaster,
															   lldb.SBProcess.eBroadcastBitStateChanged,
															   event):
					# print _.sbdbg.StateAsCString(process.GetState())
					if process.GetState() == lldb.eStateExited:
						_.state = 'EXITED'
						_.rtcode = process.GetExitStatus()
						_.stop_time = time()
						_.global_vars = _.get_globals()
						_.clear()
						break
					elif process.GetState() == lldb.eStateStopped:
						_.filter_frames()
						frame = _.get_crash_frame()
						_.crash_line = int(frame.line_entry.GetLine().__str__())
						_.rtcode = process.GetExitStatus()
						_.stop_time = time()
						_.global_vars = _.get_globals()
						# print(frame.line_entry.GetLine())
						_.state = 'STOPPED'
						# _.filter_frames()
						break

	def run(self):
		self.buff = ''
		exe = path.join(path.dirname(self.file), 'main')

		self.clear()
		dbg = lldb.SBDebugger.Create()
		dbg.SetAsync(True)
		target = dbg.CreateTargetWithFileAndArch(exe, lldb.LLDB_ARCH_DEFAULT)
		module = target.module[target.executable.basename]
		# print(target.executable.basename)
		self.miss_cnt = 0
		self.start_time = time()
		process = target.LaunchSimple(None, None, path.dirname(self.file))
		self.change_state('RUNNING')

		self.process = process
		self.target = target
		self.module = module
		self.main_thread = self.process.GetThreadAtIndex(0)
		self.sbdbg = dbg

		exit_listener = self.ExitListener()
		exit_listener._dbg = self
		exit_listener.start()
		self.exit_listener = exit_listener

	def add_buff(self):
		out = self.process.GetSTDOUT(2 ** 18)
		if out:
			# print(out.encode(), out[5:].encode())
			out = out.__str__()
			out = out.replace('\r\n', '\n')
			miss = min(self.miss_cnt, len(out))
			# print(miss)
			out = out[miss:]
			# print(':', out)
			self.miss_cnt -= miss
			self.buff += out

	def destroy(self):
		self.process.Kill()
		lldb.SBDebugger.Destroy(self.sbdbg)

	def terminate(self):
		self.process.Kill()

	def put_stdin(self, s):
		self.add_buff()
		self.process.PutSTDIN(s)
		self.miss_cnt += len(s)

	def get_output(self):
		self.add_buff()
		s = self.buff
		self.buff = ''
		return s
		
	def get_var_value(self, var_name, frame_id=None):
		if frame_id is None:
			frame = self.get_crash_frame()
		else:
			frame = self.main_thread.GetFrameAtIndex(frame_id)
		rez = frame.FindVariable(var_name).__str__()
		if rez == 'No value':
			rez = self.global_vars.get('::' + var_name, 'No value')
		return rez

	def get_runtime(self):
		return int((self.stop_time - self.start_time) * 1000)

	def get_globals(self):
		module = self.module
		target = self.target
		global_vars = dict()
		global_names = []
		for symbol in module.symbols:
			if symbol.type == lldb.eSymbolTypeData:
				global_name = symbol.name
				if global_name not in global_names:
					global_names.append(global_name)
					global_variable_list = module.FindGlobalVariables(
						target, global_name, lldb.UINT32_MAX)
					if global_variable_list:
						for global_variable in global_variable_list:
							global_vars[global_variable.name] = global_variable.__str__()	
		return global_vars

	def get_frames(self):
		frames = []
		for frame in self.main_thread.frames:
			frames.append({
				'line': frame.line_entry.GetLine().__str__(),
				'file': frame.line_entry.file.__str__(),
				'function_name': frame.GetFunctionName().__str__(),
				'desc': str(frame)[str(frame).index('`') + 1:],
				'frame_id': frame.GetFrameID().__str__()
			})	

		return frames[:100]

if len(sys.argv) > 1:
	file = sys.argv[1]
debugger = Debugger(file)


def _console_connecter(debugger):
	global decode
	global encode
	_ = debugger
	def quit():
		debugger.destroy()
		exit(0)

	def do_run():
		_.compile()
		_.run()

	def test(frame_id):
		thread = debugger.process.GetThreadAtIndex(0)
		frame = thread.GetFrameAtIndex(frame_id)
		print frame
		print frame.arguments
		print frame.get_all_variables()
		print "find results"
		print frame.FindVariable('v')


	while True:
		print(encode(input().__str__()))
		sys.stdout.flush()
		
_console_connecter(debugger)
		
