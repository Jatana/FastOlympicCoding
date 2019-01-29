'''
Scan and show compile Errors in realtime 
currently works for c++

'''


import sublime, sublime_plugin
import os
from os.path import dirname
import sys
from subprocess import Popen, PIPE
import subprocess
import shlex
from os import path
import re


from .settings import root_dir
from .settings import get_settings, get_supported_exts, is_lang_view

class InteliSenseCommand(sublime_plugin.TextCommand):
	"""
		Make intelisense with file
	"""
	run_status = ''
	timer_run = False
	REGEX_ERROR_PROP = '(:)(\d+)(:)(\d+)(:)( *)([a-zA-Z ]+)(:)( *)(.*)'

	def get_compile_cmd(self):
		run_settings = get_settings().get('run_settings', None)
		if run_settings is None: return None
		for option in run_settings:
			if option['name'] == 'C++':
				return option.get('lint_compile_cmd', None)

	def stop_sense(self):
		self.run_status = 'do_disable'

	def sync(self):
		st = self.run_status
		if self.timer_run:
			self.stop_sense()
			sublime.status_message('sense disabled')
		else:
			self.run_sense()
			sublime.status_message('sense enabled')

	def run_sense(self):
		compile_cmd = self.get_compile_cmd()
		if compile_cmd is None: return
		if not get_settings().get('lint_enabled'): return
		if self.timer_run:
			self.run_status = 'do_waited_sense'
			return 0
		self.run_status = 'do_waited_sense'
		def sense_timer(self=self):
			v = self.view
			st = self.run_status
			if st == 'do_waited_sense':
				v.erase_regions('error_marks')
				v.erase_regions('warning_marks')
				self.run_status = 'do_sense'
			elif st == 'do_sense':
				self.insert_error_marks()
				if self.run_status == 'do_sense':
					self.run_status = 'sense_complete'
			elif st == 'do_disable':
				v.erase_regions('error_marks')
				v.erase_regions('warning_marks')
				self.run_status = 'disabled'
				self.timer_run = False
				return 0
			elif st == '':
				v.erase_regions('error_marks')
				v.erase_regions('warning_marks')
				self.timer_run = False
				return 0
			sublime.set_timeout_async(sense_timer, 500)
		self.timer_run = True
		sublime.set_timeout_async(sense_timer, 500)

	def run(self, edit, action=None):
		st = self.run_status
		if action == 'run_sense':
			self.run_sense()
		elif action == 'stop_sense':
			self.stop_sense()
		elif action == 'sync_sense':
			self.sync()
		elif action == 'sync_modified':
			self.run_sense()

	def parse_cpp_errors(self, s):
		errors = []
		lst = s.split('\n')
		for i in range(0, len(lst), 1):
			try:
				words = lst[i].split()
				ind = len(words) - 1
				while ind > -1 and words[ind] != 'error:' and words[ind] != 'warning:':
					ind -= 1
				if ind < 0:
					continue
				if words[ind] == 'error:':
					is_error = True
					type = 'error'
					if words[ind - 1] == 'fatal':
						ind -= 1
				else:
					type = 'warning'
				y, x = map(int, words[ind - 1].split(':')[-3:-1])
				errors.append({
					'type': type,
					'position': (y - 1, x)
				})
			except:
				continue
		return errors

	def parse_cpp_errors_smart(self, s, run_file_path):
		errors = []
		lst = s.split('\n')
		for i in range(0, len(lst), 1):
			try:
				if lst[i][:len(run_file_path)] == run_file_path:
					s_err = lst[i][len(run_file_path):]
					sep_ind = s_err.find(':')
					# print(s_err)
					# args_err = s_err.split(':')
					# args_err = s_err[:sep_ind].split(':') + [s_err[sep_ind + 1:]]
					args_err = re.match(self.REGEX_ERROR_PROP, s_err).group(2, 4, 7, 10)
					y, x = map(int, args_err[0:2])
					type = args_err[2].rstrip().lstrip()
					error_string = args_err[3].lstrip().rstrip()
					errors.append({
						'type': self.get_preffered_type_error(type),
						'position': (y - 1, x),
						'error_string': error_string
					})
			except:
				continue
		return errors

	def get_preffered_type_error(self, error):
		error = error.rstrip().lstrip()
		if error == 'fatal error':
			return 'error'
		return error

	def insert_error_marks(self):
		v = self.view
		s = v.substr(sublime.Region(0, v.size()))
		# s = open('/Users/jatana/Desktop/cpp-cgdk/MyStrategy.cpp').read()
		run_file_path = path.join(root_dir, 'cmp_sense/amin.cpp')
		f = open(run_file_path, 'wb')
		f.write(s.encode())
		f.close()
		file_dir_path = path.split(v.file_name())[0]
		cmd = self.get_compile_cmd().format(source_file=run_file_path, source_file_dir=file_dir_path)
		process = Popen(cmd, \
				shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
		# process.wait()
		# s = process.stdout.read().decode()
		s = process.communicate()[0].decode()
		v.erase_regions('warning_marks')
		v.erase_regions('error_marks')
		try:
			errors = (self.parse_cpp_errors_smart(s, run_file_path))
		except:
			print('[FastOlympicCoding] can not parse errors')
			return 0

		for x in errors:
			if x['type'] == 'error':
				v.set_status('compile_error', ('error:%d:%d: ' + x['error_string']) \
					% (x['position'][0] + 1, x['position'][1]))
				break
		else:
			for x in errors:
				if x['type'] == 'warning':
					v.set_status('compile_error', ('error:%d:%d: ' + x['error_string']) \
						% (x['position'][0] + 1, x['position'][1]))
					break
			else:
				v.erase_status('compile_error')

		warn_regions = []
		for x in errors:
			if x['type'] == 'warning':
				pt = v.text_point(*x['position'])
				warn_regions.append(v.word(pt))

		error_regions = []
		for x in errors:
			if x['type'] == 'error':
				pt = v.text_point(*x['position'])
				error_regions.append(v.word(pt))
		
		if self.run_status == 'do_sense':
			self.view.add_regions(
				'warning_marks',
				warn_regions,
				get_settings().get('lint_warning_region_scope', 'text.plain'),
				'dot',
				sublime.DRAW_NO_FILL
			)
			self.view.add_regions(
				'error_marks',
				error_regions,
				get_settings().get('lint_error_region_scope', 'text.plain'),
				'dot',
				sublime.DRAW_NO_FILL
			)

class SenseListener(sublime_plugin.EventListener):
	def __init__(self):
		super(SenseListener, self).__init__()

	# def on_post_save_async(self, view):
	# 	if get_syntax(view) == 'cpp':
	# 		view.run_command('inteli_sense', {'action': 'run_sense'})

	def on_load(self, view):
		if is_lang_view(view, 'C++'):
			view.run_command('inteli_sense', {'action': 'run_sense'})

	def on_pre_close(self, view):
		if is_lang_view(view, 'C++'):
			view.run_command('inteli_sense', {'action': 'stop_sense'})

	def on_modified(self, view):
		if is_lang_view(view, 'C++'):
			view.run_command('inteli_sense', {'action': 'sync_modified'})

	def on_deactivated(self, view):
		if is_lang_view(view, 'C++'):
			view.run_command('inteli_sense', {'action': 'stop_sense'})

	def on_activated(self, view):
		if is_lang_view(view, 'C++'):
			view.run_command('inteli_sense', {'action': 'run_sense'})