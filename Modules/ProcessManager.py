import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
from os import path
import shlex


class ProcessManager(object):
	def __init__(self, file, syntax, run_options=None):

		super(ProcessManager, self).__init__()
		self.syntax = syntax
		self.file = file
		self.is_run = False
		self.test_counter = 0

		self.run_options = run_options

		# Old compile parameters
		# new in settings.py
		#

		python_path = '/Library/Frameworks/Python.framework/Versions/3.4/bin/python3'
		self.compile_cmds = {
			'source.python': None,
			'source.c++': lambda name: 'g++ -std=gnu++11 ' +'"'+name+'"',
			'source.pascal': lambda name: '/usr/local/bin/ppc386 ' + '"' + name + '"' 
		}

		self.run_cmds = {
			'source.python': \
				lambda name: python_path + ' ' +'"'+name+'"',
			'source.c++': lambda name: './a.out -debug',
			'source.pascal': lambda name: '"'+name[:-4]+'"'
			#'./' + '"'+name[:-4]+'"'
		}

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

	def get_compile_cmd(self):
		opt = self.run_options
		file_ext = path.splitext(self.file)[1][1:]
		for x in opt:
			if file_ext in x['extensions']:
				if x['compile_cmd'] is None:
					return None
				return x['compile_cmd'](self.file)
		else:
			return -1

	def get_run_cmd(self):
		opt = self.run_options
		file_ext = path.splitext(self.file)[1][1:]
		for x in opt:
			if file_ext in x['extensions']:
				if x['run_cmd'] is None:
					return None
				return x['run_cmd'](self.file)
		else:
			return -1

	def compile(self, wait_close=True):
		cmd = self.get_compile_cmd()
		if cmd is not None:
			# cmd = cmd(self.file)
			# print(cmd)
			PIPE = subprocess.PIPE
			#cwd=os.path.split(self.file)[0], \
			p = subprocess.Popen(cmd, \
				shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, \
					cwd=os.path.split(self.file)[0])
			if wait_close:
				p.wait()
			return (p.returncode, p.stdout.read().decode())



	def run_file(self):
		if self.is_run and False:
			raise AssertionError('cant run process because is already running')
		cmd = self.get_run_cmd()
		# print(cmd)
		PIPE = subprocess.PIPE
		self.process = subprocess.Popen(cmd, \
			shell=True, stdin=PIPE, stdout=PIPE, \
				stderr=subprocess.STDOUT, bufsize=0, cwd=os.path.split(self.file)[0])
	
	def insert(self, s):
		if self.process.poll() is None:
			# print(s)
			self.process.stdin.write(s.encode())

	def is_stopped(self):
		return self.process.poll()

	def get_output(self):
		return self.process.stdout.read().decode()

	def new_test(self, input_data=None):
		self.test_counter += 1
		# self.process.terminate()
		# self.process.kill()
		self.run_file()
		if input_data != None:
			self.insert(input_data)

	def terminate(self):
		try:
			self.process.kill()
			self.process.terminate()
		except:
			pass