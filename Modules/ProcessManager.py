from os.path import dirname
from os import path
from subprocess import Popen, PIPE
import os
import sys
import subprocess
import shlex
import signal
import sublime

class ProcessManager(object):
	def __init__(self, file, syntax, run_settings=None):

		super(ProcessManager, self).__init__()
		self.syntax = syntax
		self.file = file
		self.is_run = False
		self.test_counter = 0
		self.write = self.insert
		self.run = self.run_file
		self.run_settings = run_settings
		self.file_name = path.splitext(path.split(file)[1])[0]

	def get_path(self, lst):
		rez = ''
		for x in lst:
			if x[0] == '-':
				rez += ' ' + x
			elif x[0] == '.':
				rez += x
			else:
				rez += ' "' + x + '" '
		return rez

	def format_command(self, cmd, args=''):
		file = path.split(self.file)[1]
		return cmd.format(
			file=file,
			source_file=self.file,
			source_file_dir=path.dirname(self.file),
			file_name=self.file_name,
			args=args
		)

	def has_var_view_api(self):
		return False

	def get_compile_cmd(self):
		opt = self.run_settings
		file_ext = path.splitext(self.file)[1][1:]
		for x in opt:
			if file_ext in x['extensions']:
				if x['compile_cmd'] is None:
					return None
				return self.format_command(x['compile_cmd'])
		else:
			return -1

	def get_run_cmd(self, args):
		opt = self.run_settings
		file_ext = path.splitext(self.file)[1][1:]
		for x in opt:
			if file_ext in x['extensions']:
				if x['run_cmd'] is None:
					return None
				return self.format_command(x['run_cmd'], args=args)
		else:
			return -1

	def compile(self, wait_close=True):
		cmd = self.get_compile_cmd()
		if cmd is not None:
			PIPE = subprocess.PIPE
			p = subprocess.Popen(cmd, \
				shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, \
					cwd=os.path.split(self.file)[0])
			compile_result = p.communicate()[0].decode('utf-8', 'ignore')
			return (p.returncode, compile_result)

	def run_file(self, args=[]):
		if self.is_run and False:
			raise AssertionError('cant run process because is already running')
		cmd = self.get_run_cmd(' '.join(args))
		
		self.is_run = False
		PIPE = subprocess.PIPE
		preexec_fn = None

		if sublime.platform() == 'windows':
			use_shell = False
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			preexec_fn = None
		else:
			startupinfo = None
			use_shell = True
			preexec_fn = os.setsid

		self.process = subprocess.Popen(
			cmd,
			shell=use_shell,
			stdin=PIPE,
			stdout=PIPE,
			stderr=subprocess.STDOUT,
			bufsize=0,
			cwd=os.path.split(self.file)[0],
			startupinfo=startupinfo,
			preexec_fn=preexec_fn,
			universal_newlines=True
		)
	
	def insert(self, s):
		if self.process.poll() is None:
			self.process.stdin.write(s)
			self.process.stdin.flush()

	def communicate(self, s, timeout=None):
		return self.process.communicate(input=s, timeout=timeout)

	def is_stopped(self):
		return self.process.poll()

	def read(self, bfsize=None):
		if bfsize is None:
			return self.process.stdout.read()
		else:
			return self.process.stdout.read(bfsize)

	def new_test(self, input_data=None):
		self.test_counter += 1
		self.run_file()
		if input_data != None:
			self.insert(input_data)

	def terminate(self):
		if sublime.platform() == 'linux':
			os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
		else:
			self.process.kill()