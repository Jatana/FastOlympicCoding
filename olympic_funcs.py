import sublime, sublime_plugin
import os
from os import listdir
from os.path import dirname
import sys
from sublime import Region
from os import path


from .Modules.ProcessManager import ProcessManager
from .settings import root_dir, base_name, settings_file, default_settings_file, \
			get_settings, is_run_supported_ext
from .Modules.ClassPregen.ClassPregen import gen as gen_template


class OlympicFuncsCommand(sublime_plugin.TextCommand):
	ROOT = dirname(__file__)

	def run(self, edit, action=None, clr_tests=False,
			text=None, sync_out=True, reselect=False, smart_fold=False):
		v = self.view
		scope_name = v.scope_name(v.sel()[0].begin()).rstrip()
		file_syntax = scope_name.split()[0]

		if action == 'insert':
			if reselect:
				v.replace(edit, v.sel()[0], text)
				v.unfold(v.sel()[0])
				if smart_fold:
					row_high, col = v.rowcol(v.sel()[0].b)
					row_low, _ = v.rowcol(v.sel()[0].a)
					row_high = min(row_high, row_low + 15)
					v.fold(Region(v.text_point(row_high, col), v.sel()[0].b))
			else:
				v.insert(edit, v.sel()[0].begin(), text)
			
		elif action == 'insert_template':
			w_sel = v.word(v.sel()[0])
			func = v.substr(v.word(w_sel)).strip()
		
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
				v.run_command('insert_best_completion', {'exact': False, 'default': '\t'})
		
		elif action == 'show_funcs':
			wind = v.window()
			funcs = listdir(path.join(root_dir, get_settings().get('algorithms_base')))
			def collect_all(base, lst, codes, prefix=''):
				files = listdir(base)
				for file in files:
					if path.isfile(path.join(base, file)):
						if file[-4:] == '.cpp':
							lst.append(prefix + '/' + file)
							codes.append(path.join(base, file))
					elif path.isdir(path.join(base, file)):
						if file != '.git':
							lst.append(prefix + '/' + file + ' ->')
							codes.append(path.join(base, file))
							collect_all(path.join(base, file), lst, codes, prefix='\t' + prefix + ('/' if prefix else '*') + file)
			all, codes = [], []
			collect_all(path.join(root_dir, get_settings().get('algorithms_base')), all, codes)
			to_view_funcs = [x[:-4] for x in funcs if x[-4:] == '.cpp']
			def on_done(ind, funcs=funcs, initial=v.substr(v.sel()[0])):
				if ind == -1:
					self.view.run_command('olympic_funcs', {'text': initial, 'action': 'insert', 'reselect': True})
					return

			def on_highlight(ind, codes=codes, edit=edit, view=v):
				if path.isfile(codes[ind]):
					code = open(codes[ind], 'r', encoding='utf-8').read()
					v.run_command('olympic_funcs', {'text': code,
							'action': 'insert', 'reselect': True, 'smart_fold': True})

			wind.show_quick_panel(all, on_done, 1, 0, on_highlight)

		elif action == 'open_settings':
			v.window().run_command('new_window')
			sublime.active_window().set_sidebar_visible(False)
			
			sublime.active_window().open_file(path.join(root_dir, default_settings_file))
			sublime.active_window().set_layout({
				'cols': [0, 0.5, 1],
				'rows': [0, 1],
				'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
			})
			_opt_path = path.join(sublime.packages_path(), 'User', 'FastOlympicCoding.sublime-settings')
			if not path.exists(_opt_path):
				_opt = open(_opt_path, 'w')
				_opt.write('{\n\t\n}')
				_opt.close()

			_opt_view = sublime.active_window().open_file(_opt_path)
			sublime.active_window().set_view_index(_opt_view, 1, 0)

class GenListener(sublime_plugin.EventListener):
	"""docstring for GenListener"""

	def try_expand(self, prefix):
		return gen_template(prefix, get_settings().get('cpp_complete_settings'))
			
	def on_text_command(self, view, command_name, args):
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
