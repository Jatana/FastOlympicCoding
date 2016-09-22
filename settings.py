import sublime
from os import path
import os



# plugin name dont change it!
plugin_name = 'FastOlympicCoding'


# root_dir = path.join(sublime.packages_path(), plugin_name + '/')
root_dir = path.split(__file__)[0]
if path.split(root_dir)[1] != plugin_name:
	os.rename(root_dir, path.join(path.split(root_dir)[0], plugin_name))


# Error Highlighter Settings
# please restart plugin after you changes

error_region_scope = 'variable.c++'
# error_region_scope = 'invalid.illegal'
warning_region_scope = 'constant'

# Compile Options
run_options = [
	{
		'name': 'C++',
		'extensions': ['cpp'],
		'compile_cmd': lambda name: ('g++ "%s" -std=gnu++11' % name),
		'run_cmd': lambda name: './a.out -debug'
	},

	{
		'name': 'Python',
		'extensions': ['py'],
		'compile_cmd': None,
		'run_cmd': lambda name: ('/Library/Frameworks/Python.framework/Versions/3.4/bin/python3 "%s"' % name)
		# 'run_cmd': lambda name: ('python3 "%s"' % name)
	},

	{
		'name': 'Pascal',
		'extensions': ['pas'],
		'compile_cmd': lambda name: '/usr/local/bin/ppc386 "%s"' % name,
		'run_cmd': lambda name: '"' + name[:-4] + '"'
	},

	{
		'name': 'CSharp',
		'extensions': ['cs'],
		'compile_cmd': lambda name: '/usr/local/bin/mcs "%s"' % name,
		'run_cmd': lambda name: '/usr/local/bin/mono "' + path.splitext(name)[0] + '.exe"'
	}
]