import sublime
from os import path
from FastOlympicCoding.settings import root_dir


def plugin_loaded():
	rm_in = open(path.join(root_dir, 'system_settings.json'))
	sys_settings = sublime.decode_value(rm_in.read())
	rm_in.close()

	if not sys_settings['is_init']:
		sys_settings['is_init'] = True
		rm_out = open(path.join(root_dir, 'system_settings.json'), 'w')
		rm_out.write(sublime.encode_value(sys_settings))
		rm_out.close()
		sublime.windows()[0].open_file(path.join(root_dir, 'Docs/Docs-EN.md'))


class SysManager:
	def is_sidebar_open(w):
		window = sublime.active_window()
		view = window.active_view()
		if view:
			sel1 = view.sel()[0]
			window.run_command('focus_side_bar')
			print(window.active_view())
			window.run_command('move', {"by": "characters", "forward": True})
			sel2 = view.sel()[0]
			if sel1 != sel2:
				window.run_command('move', {"by": "characters", "forward": False})
				return False # print('sidebar is closed')
			else:
				group, index = window.get_view_index(view)
				window.focus_view(view)
				window.focus_group(group)
				return True # print('sidebar is open')
		print('i dont know')
		return True # by default assume it's open if no view is opened
