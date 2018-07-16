import sublime
from .debugger_info import Debugger

import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
from os import path
import shlex
import select
import re


class LLDBDebugger(Debugger):
	"""
	LLDBDebugger debug cpp programs with 
	lldb
	"""	

	RUN_PRIOR = 0.5


	READ_LIMIT = 2 ** 19
	

	class LLDBAnalyzer(object):
		"""docstring for LLDBAnalyzer"""

		STR_REGEX_CRASH_LINE = '((?:{name}:))(\d+)'
		REGEX_RT_CODE = re.compile('(?:\(code=)([A-Za-z0-9_]+)')
		REGEX_STOP_REASON = re.compile('(?:stop reason = )([a-zA-Z_]+)')


		def __init__(self, on_status_change):
			super(LLDBDebugger.LLDBAnalyzer, self).__init__()
			self.data = ''
			self.data_buff = ''
			self.status = 'LAUNCHING'
			self.proc_state = 'LAUNCHING'
			self.change_status = on_status_change
			self.change_status(self.status)

		def add_out(self, out):
			self.data += out
			self.data_buff += out

		def encode_save(self, str):
			unsave = '.\\{}()[]'
			rez = ''
			for x in str:
				if x in unsave:
					rez += '\\'
				rez += x
			return rez

		def analyze(self):
			status = self.status
			buff = self.data_buff
			self.change_status(self.proc_state)
			if status == 'LAUNCHING':
				p_ind = buff.find('Process')
				if p_ind == -1:
					return 'NEED_MORE'
				self.pid = int(buff[p_ind:].split()[1])
				self.status = 'RUNNING'
				self.proc_state = 'RUNNING'
				self.data_buff = ''
			elif status == 'RUNNING':
				p_ind = buff.find('Process')
				if p_ind == -1:
					return 'NEED_MORE'
				self.pid = int(buff[p_ind:].split()[1])
				state = buff[p_ind:].split()[2]
				if state == 'stopped':
					self.status = 'CRASHED'
					self.proc_state = 'CRASHED'
					self.rtcode = 228
					# print('FINALLY CRASHED')
				else:
					self.rtcode = buff[p_ind:].split()[6]
					self.status = 'STOPPED'
					self.proc_state = 'STOPPED'
					# print('rtcode -> ', self.rtcode)
			elif status == 'FINDING_CRASHLINE':
				# print('finding crash_line')
				file = path.split(self._file_crash)[1]
				# self.regex_crash_line = re.compile('\\.cpp:(\d+)')
				self.crash_line = self.regex_crash_line.search(self.data_buff)
				if self.crash_line is None:
					# print('REASON crashline NOT FOUND')
					return 'NEED_MORE'
				self.crash_line = int(self.crash_line.group(2))
				# print(self.crash_line)
				self.rtcode = self.REGEX_RT_CODE.search(self.data_buff)
				if self.rtcode is None:
					self.rtcode = '-'
				else:
					self.rtcode = self.rtcode.group(1)
				self.stop_reason = self.REGEX_STOP_REASON.search(self.data_buff)
				if self.stop_reason is None:
					# print('REASON stop reason NOT FOUND')
					return 'NEED_MORE'
				self.stop_reason = self.stop_reason.group(1)
				self.proc_state = 'CRASHED, stop reason = %s' % self.stop_reason
				self.status = 'CRASHLINE_FOUND'
				self.data_buff = ''
			self.change_status(self.proc_state)

		def proc_stopped(self):
			return self.status in {'CRASHED', 'STOPPED'}

		def find_crashline(self, file):
			self.status = 'FINDING_CRASHLINE'
			self._file_crash = path.split(file)[1]
			self.regex_crash_line = re.compile( \
				self.STR_REGEX_CRASH_LINE.format(name=self.encode_save(self._file_crash)))
			# print(self.STR_REGEX_CRASH_LINE.format(name=self.encode_save(self._file_crash)))


	supported_exts = ['cpp']

	def __init__(self, file):
		# super(LLDBDebugger, self).__init__(file)
		self.file = file
		self.in_buff = ''
		self.on_status_change = None

	def is_runnable():
		return sublime.platform() == 'osx'

	def has_var_view_api(self):
		return True

	def compile(self):
		cmd = 'g++ -std=gnu++11 -g -o main "%s"' % self.file
		PIPE = subprocess.PIPE
		# print(dir(self))
		if self.on_status_change is not None:
			self.on_status_change('COMPILING')
		#cwd=os.path.split(self.file)[0], \
		p = subprocess.Popen(cmd, \
			shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, \
				cwd=os.path.split(self.file)[0])
		p.wait()
		return (p.returncode, p.stdout.read().decode())


	def run(self, args=' -debug'):
		self.analyzer = LLDBDebugger.LLDBAnalyzer(self.on_status_change)
		cmd = 'lldb main'
		PIPE = subprocess.PIPE
		#cwd=os.path.split(self.file)[0], \
		process = subprocess.Popen(cmd, \
			shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, \
				cwd=os.path.split(self.file)[0])
		self.process = process
		self.miss_cnt = 0
		out_file = path.join(path.split(self.file)[0], 'output.txt')
		f = open(out_file, 'w')
		f.write('')
		f.close()
		cmd = 'process launch -o output.txt -- %s\n' % args
		# cmd = 'process launch  -- %s\n' % args
		process.stdin.write(cmd.encode('utf-8'))
		process.stdin.flush()
		# self.miss_cnt += len(cmd)
		self.need_out = True
		# self.write('123\n')
		sublime.set_timeout_async(self.__process_listener)
		# process.stdin.write('123\n'.encode('utf-8'))
		# process.stdin.flush()

		# return "END"
		# return process.stdout.read(4096).decode()

	def __on_out(self, s):
		# if self.miss_cnt > 0:
		# 	self.miss_cnt -= 1
		# 	return None
		analyzer = self.analyzer
		proc = self.process
		# print(s, end='')
		self.analyzer.add_out(s)
		if s == '\n':
			self.analyzer.analyze()
		if self.analyzer.status == 'RUNNING':
			self.write(self.in_buff)
			self.in_buff = ''
		elif self.analyzer.proc_stopped():
			if analyzer.status == 'CRASHED':
				analyzer.find_crashline(self.file)
				proc.stdin.write('bt\n'.encode('utf-8'))
				proc.stdin.flush()
		if analyzer.status == 'CRASHLINE_FOUND':
			self.need_out = False
			proc.stdin.write('process kill\n'.encode('utf-8'))
			proc.stdin.flush()
			proc.stdin.write('exit\n'.encode('utf-8'))
			proc.stdin.flush()
			proc.wait()
			# print(proc.stdout.read().decode())
			# print(analyzer.crash_line)
			file_out = open(path.join(path.dirname(self.file), 'output.txt'))
			output = file_out.read(self.READ_LIMIT)
			# print('Hello i am here the out size ->', len(output))
			file_out.close()
			# print('out -> ', output)
			self.on_out(output)
			self.on_stop(analyzer.rtcode, crash_line=analyzer.crash_line)
		elif analyzer.status == 'STOPPED':

			proc.terminate()
			proc.kill()
			# print(self.file)
			output = open(path.join(path.dirname(self.file), 'output.txt')).read(self.READ_LIMIT)
			if len(output) > self.READ_LIMIT:
				output = "<to big>" + output[-self.READ_LIMIT:]
			self.on_out(output)
			self.on_stop(analyzer.rtcode)


		#sys.stdout.flush()

	def __process_listener(self):
		proc = self.process
		while proc.returncode is None:
			s = proc.stdout.read(1).decode()
			if s and self.need_out:
				if self.miss_cnt > 0:
					self.miss_cnt -= 1
					continue
				self.__on_out(s)
			else:
				return None

	def set_calls(self, on_out, on_stop, on_status_change):
		'''
		please set calls
		and calls on program out or stop
		sample 
			on_out(s, is_err=False)
			on_stop(rtcode, crash_line=None)
		'''
		# print('!!!!! CALLS SET')
		self.on_out = on_out
		self.on_stop = on_stop
		self.on_status_change = on_status_change

	def write(self, s):
		if self.analyzer.status == 'RUNNING':
			self.miss_cnt += len(s)
			self.process.stdin.write(s.encode('utf-8'))
			self.process.stdin.flush()
		else:
			self.in_buff += s
			# print(self.in_buff)

	def terminate(self):
		proc = self.process
		proc.send_signal(2)
