import sublime, sublime_plugin
import os
from os import listdir
from os.path import dirname
import sys
from sublime import Region
from os import path


from .Modules.ProcessManager import ProcessManager
from .settings import root_dir, base_name, settings_file, \
			get_settings, is_run_supported_ext
from .Modules.ClassPregen.ClassPregen import gen as gen_template


class PreGenParser(object):
	"""docstring for PreGenParser"""
	match_open_bracket = {
		')': '(',
		'}': '{',
		']': '['
	}
	def __init__(self, s):
		super(PreGenParser, self).__init__()
		self.s = s
	
	def is_word(self, c):
		return c == '_' or ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z')

	def is_number(self, c):
		return ord('0') <= ord(c) <= ord('9')

	def left_bracket(self, ind, full_result=False):
		s = self.s
		bracket = s[ind]
		if bracket in {')', '}', ']'}:
			i = ind - 1
			while i >= 0:
				if s[i] == self.match_open_bracket[bracket]:
					return i
				elif s[i] in self.match_open_bracket.keys():
					i = self.left_bracket(i)
					i -= 1
				elif s[i] in {"'", '"'}:
					i = self.left_bracket(i)
					i -= 1
				else:
					i -= 1
			return -1
		elif bracket == '"' or bracket == "'":
			i = ind - 1
			while i >= 0:
				if s[i] == bracket:
					j = i - 1
					cnt = 0
					while j >= 0 and s[j] == '\\':
						cnt += 1
						j -= 1
					if cnt % 2 == 0:
						return i
					i -= 1
					continue
				else:
					i -= 1
			return -1
		else:
			"This condition should not be performed"
			return -1

	def get_first_symb(self, i, k):
		s = self.s
		while i >= 0 and (s[i] in {' ', '\t'}) and i < len(s):
			i += k
		if i >= 0 and i < len(s) and s[i] != ' ' and s[i] != '\t':
			return i
		return None

	def parse(self):
		s = self.s
		pt_right = len(s)
		i = len(s) - 1
		rez = []
		while i >= 0:
			if s[i] == ' ':
				right = self.get_first_symb(i, 1)
				left = self.get_first_symb(i, -1)
				if right is None or left is None:
					i -= 1
					continue
				if self.is_word(s[left]) or self.is_number(s[left]) or s[left] == ')':
					if self.is_word(s[right]) or self.is_number(s[right]) or s[right] == '(':
						rez.append(sublime.Region(right, pt_right))
						pt_right = left + 1
						i = left
						continue
			i -= 1
		if s[:pt_right].rstrip().lstrip() != '':
			rez.append(sublime.Region(self.get_first_symb(0, 1), pt_right))
		rez.reverse()
		return rez


class PreProc(object):
	"""docstring for PreProc"""
	def f(*args, indent=''):
		def get_for_str(iter, begin, end, k, indent=indent):
			return 'for (int {0} = {1}; {0} < {2}; {0}{3}) '.format(iter, begin, end, k) + \
				'{\n' + indent + '\t'
		left_prototype = 'for (int {0} = {1}; {0} < {2}; {0}{3}) {\n' + indent + '\t'
		right_prototype = '\n' + indent + '}'
		if len(args) == 0:
			return get_for_str('i', '0', 'n', '++'), right_prototype
		if len(args) == 1:
			return get_for_str('i', '0', args[0], '++'), right_prototype
		if len(args) == 2:
			return get_for_str(args[0], '0', args[1], '++'), right_prototype

		left_prototype = 'fk (%s, %s, %s, %s) {\n' + indent + '\t'
		right_prototype = '\n' + indent + '}'
		if len(args) == 3:
			return get_for_str(args[0], args[1], args[2], '++'), right_prototype
		if len(args) == 4:
			return get_for_str(args[0], args[1], args[2], ' += ' + args[3]), right_prototype

	def fr(*args, indent=''):
		def get_for_str(iter, begin, end, k, indent=indent):
			return 'for (int {0} = {1}; {0} > {2}; {0}{3}) '.format(iter, begin, end, k) + \
				'{\n' + indent + '\t'
		left_prototype = 'for (int {0} = {1}; {0} > {2}; {0}{3}) {\n' + indent + '\t'
		right_prototype = '\n' + indent + '}'
		if len(args) == 0:
			return get_for_str('i', '-1', 'n', '--'), right_prototype
		if len(args) == 1:
			return get_for_str('i', '-1', args[0], '--'), right_prototype
		if len(args) == 2:
			return get_for_str(args[0], args[1], '-1', '--'), right_prototype

		left_prototype = 'fk (%s, %s, %s, %s) {\n' + indent + '\t'
		right_prototype = '\n' + indent + '}'
		if len(args) == 3:
			return get_for_str(args[0], args[1], args[2], '--'), right_prototype
		if len(args) == 4:
			return get_for_str(args[0], args[1], args[2], ' -= ' + args[3]), right_prototype



class OlympicFuncsCommand(sublime_plugin.TextCommand):
	ROOT = dirname(__file__)
	ruler_opd_panel = 0.8
	pregen_funcs = {
		'f': {
			'func': PreProc.f
		},
		'fr': {
			'func': PreProc.fr
		}
	}

	have_tied_dbg = False

	def create_opd(self, clr_tests=False, sync_out=True):
		'''
		creates opd with supported language
		'''
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		# v.window().show_input_panel("Runned", "123", \
		# 	self.DebugArea.on_done, self.DebugArea.on_change, self.DebugArea.on_cancel)
		# v.window().show_quick_panel(["5"], \
		# 	1, 1, 1, 1)
		window = v.window()
		# opd_view = window.create_output_panel("opd_view")
		# print(opd_view.settings().get('syntax'))
		# window.run_command('show_panel', {'panel': 'output.opd_view'})
		
		if self.have_tied_dbg:
			prop = (window.get_view_index(self.tied_dbg))
			if prop == (-1, -1):
				need_new = True
			else:
				need_new = False
		else:
			need_new = True
		if not need_new:
			dbg_view = self.tied_dbg
			out_view = self.out_view
			create_new = False
		else:
			dbg_view = window.new_file()
			out_view = window.new_file()
			self.tied_dbg = dbg_view
			self.tied_out = out_view
			self.have_tied_dbg = True
			create_new = True
			dbg_view.run_command('toggle_setting', {'setting': 'line_numbers'})
			# dbg_view.run_command('toggle_setting', {"setting": "gutter"})
			try:
				sublime.set_timeout_async(lambda window=window: window.set_sidebar_visible(False), 50)
			except:
				# Version of sublime text < 3102
				pass
			dbg_view.run_command('toggle_setting', {'setting': 'word_wrap'})

		window.set_layout({
			'cols': [0.0, 0.3333333333333333, 0.6666666666666666, 1.0],
			'rows': [0, 1],
			'cells': [[0, 0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1]]
		})

		window.set_view_index(dbg_view, 1, 0)
		window.set_view_index(out_view, 0, 0)
		window.focus_view(v)
		window.focus_view(dbg_view)
		# opd_view.run_command('erase_view')
		dbg_view.set_syntax_file('Packages/%s/OPDebugger.tmLanguage' % base_name)
		dbg_view.set_name(os.path.split(v.file_name())[-1] + ' -run')
		out_view.set_name(os.path.split(v.file_name())[-1] + ' [output]')
		dbg_view.run_command('test_manager', \
			{'action': 'make_opd', 'build_sys': file_syntax, 'run_file': v.file_name(), \
			'clr_tests': clr_tests, 'sync_out': sync_out})
	
	def close_opds(self):
		w = self.view.window()
		for v in w.views():
			# if v.get_status('opd_info') == 'opdebugger-file':
			# print(v.name()[::-1][:len('-run')][::-1])
			if v.name()[::-1][:len('-run')][::-1] == '-run':
				v.close()

	def insert_pregen_class(self, edit):
		view = self.view
		w_sel = view.word(view.sel()[0])
		word = view.substr(w_sel).lstrip().rstrip()
		pregen = pregen_class(word)
		if pregen:
			view.replace(edit, w_sel, pregen + ' ')
		else:
			view.run_command('insert_best_completion', {
				'exact': False,
				'default': '\t'
			})


	def run(self, edit, action=None, clr_tests=False, text=None, sync_out=True, func_name=None):
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]
		if action == 'can_pregen_classes':
			return False
		if action == 'insert':
			v.insert(edit, v.sel()[0].begin(), text)
		if action == 'fast_gen':
			sel = v.sel()[0]
			text_sel = v.line(sel)
			text = v.substr(text_sel)
			p = PreGenParser(v.substr(text_sel))
			parsed = (p.parse())
			begin_pt = text_sel.begin()
			proc_pt = sublime.Region(begin_pt + parsed[0].begin(), text_sel.end())
			f = self.pregen_funcs[text[parsed[0].begin():parsed[0].end()]]['func']
			prev_text = text[:parsed[0].begin()]
			parms = []
			for i in range(1, len(parsed)):
				parms.append(text[parsed[i].begin():parsed[i].end()])

			first_unit, second_unit = f(*parms, indent=prev_text)
			v.replace(edit, proc_pt, first_unit + second_unit)
			v.sel().clear()
			x = proc_pt.begin() + len(first_unit)
			if v.settings().get('translate_tabs_to_spaces'):
				x = x - 1 + v.settings().get('tab_size')
			v.sel().add(sublime.Region(x, x))

			
		elif action == 'gen_def':
			func = func_name
			pt = v.sel()[0].begin()
			cursor = v.sel()[0]
			if v.scope_name(pt).rstrip() != 'source.c++':
				v.run_command('insert_best_completion', {
					'exact': False,
					'default': '\t'
				})
				return None
			w_sel = v.word(cursor)
			if not w_sel.empty():
				func = v.substr(w_sel).lstrip().rstrip()
			if func:
				if len(func.lstrip().rstrip()) != 0:
					insert_snippet = get_settings().get('algorithms_base') and \
						path.isfile(path.join(
							root_dir,
							get_settings().get('algorithms_base'),
							func + '.cpp')
						)
					if insert_snippet:
						f = open(path.join(root_dir, get_settings().get('algorithms_base'), func + '.cpp'), encoding='utf-8')
						v.replace(edit, w_sel, f.read())
						f.close()
						prop_path = path.join(
							root_dir,
							get_settings().get('algorithms_base'),
							func + '.cpp:properties'
						)
						if path.isfile(prop_path):
							f_prop = open(prop_path, 'r')
							prop = sublime.decode_value(f_prop.read())
							if prop.get('fold', None) is not None:
								for x in prop['fold']:
									v.fold(Region(w_sel.a + x[0], w_sel.a + x[1]))
							if prop.get('move_cursor', None) is not None:
								v.show_at_center(w_sel.a + prop['move_cursor'])
								v.sel().clear()
								v.sel().add(Region(w_sel.a + prop['move_cursor'], w_sel.a + prop['move_cursor']))
					else:
						# try do vvvii
						self.insert_pregen_class(edit)

				else:
					v.insert(edit, cursor.a, '\t')
			else:
				v.insert(edit, cursor.a, '\t')
		elif action == 'insert_pregen_class':
			self.insert_pregen_class(edit)
			
		elif action == 'make_opd':
			self.close_opds()
			self.create_opd(clr_tests=clr_tests, sync_out=sync_out)
		elif action == 'show_funcs':
			wind = v.window()
			funcs = listdir(path.join(root_dir, get_settings().get('algorithms_base')))
			to_view_funcs = [x[:-4] for x in funcs if x[-4:] == '.cpp']
			def on_done(ind, funcs=funcs):
				if ind == -1:
					return 0
				f = open(path.join(root_dir, get_settings().get('algorithms_base'), funcs[ind]))
				self.view.run_command('olympic_funcs', {'text': f.read(), 'action': 'insert'})
				f.close()

			wind.show_quick_panel(to_view_funcs, on_done, 1, 0, 1)
		elif action == 'sync_opdebugs':
			w = v.window()
			layout = w.get_layout()

			if len(layout['cols']) == 3:
				if layout['cols'][1] != 1:
					# hide opd panel
					self.ruler_opd_panel = min(layout['cols'][1], 0.93)
					layout['cols'][1] = 1
					w.set_layout(layout)
				else:
					# show opd panel
					layout['cols'][1] = self.ruler_opd_panel
					need_x = self.ruler_opd_panel
					w.set_layout(layout)
			# w.run_command('toggle_side_bar')
		elif action == 'open_settings':
			self.view.window().open_file(path.join(root_dir, settings_file))

class GenListener(sublime_plugin.EventListener):
	"""docstring for GenListener"""

	def try_expand(self, prefix):
		return gen_template(prefix, get_settings().get('cpp_complete_settings'))
			
	def on_text_command(self, view, command_name, args):
		if command_name == 'olympic_funcs':
			if args['action'] == 'insert_pregen_class':
				sel = view.sel()[0]
				text_sel = view.line(sel)
				text = view.substr(text_sel)
				text = text.rstrip().lstrip()
				if view.match_selector(view.sel()[0].a, 'meta.function.parameters.c++'):
					reg = "[ ,(]"
					match = re.search(reg, text[-1::-1])
					text = text[-match.start():]
					# print (text)
					reg = "[ ,)]"
					match = re.search(reg, text)
					text = text[:match.start()]
					# print (text)
				if pregen_class(text) is None:
					print('invoke')
					return ('insert_best_completion', {'exact': False, 'default': '\t'})
			# elif args['action'] == 'gen_def':
				# if get_settings().get('algorithms_base', None) is None:
					# return ('insert_best_completion', {'exact': False, 'default': '\t'})

		if command_name == 'view_tester':
			ext = path.splitext(view.file_name())[1][1:]
			if args['action'] == 'make_opd':
				if not is_run_supported_ext(ext):
					return ('olympic_funcs', { 'action': 'pass' })
			elif args['action'] == 'toggle_using_debugger':
				if ext != 'cpp':
					return ('olympic_funcs', { 'action': 'pass' })

	def on_modified(self, view):
		if not len(view.sel()) or view.scope_name(view.sel()[0].a).find('source.c') == -1: return

		prefix = view.substr(view.word(view.sel()[0]))
		if len(prefix) <= 1: return
		
		if self.try_expand(prefix):
			print('invoking')
			view.run_command('hide_auto_complete')
			def run():
				view.run_command('auto_complete', {
					'disable_auto_insert': True,
					'next_completion_if_showing': False,
					'auto_complete_commit_on_tab': True
				})
			sublime.set_timeout(run)

	def on_query_completions(self, view, prefix, locations):
		if not get_settings().get('cpp_complete_enabled'): return
		if len(prefix) == 1: return
		expand = self.try_expand(prefix)
		if (view.scope_name(view.sel()[0].a).find('source.c') != -1) and expand:
			if prefix == expand: return []
			return [(prefix + '\t' + expand, expand)]
		return []
