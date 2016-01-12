import sublime
from os import path
from SublimeFastOlympicCoding.settings import root_dir

rm_in = open(path.join(root_dir, 'system_settings.JSON'))
sys_settings = sublime.decode_value(rm_in.read())
rm_in.close()

if not sys_settings['is_init']:
	sys_settings['is_init'] = True
	rm_out = open(path.join(root_dir, 'system_settings.JSON'), 'w')
	rm_out.write(sublime.encode_value(sys_settings))
	rm_out.close()
	sublime.windows()[0].open_file(path.join(root_dir, 'README.md'))




