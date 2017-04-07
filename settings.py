import sublime
from os import path
import os


plugin_name = 'FastOlympicCoding'
algorithms_base = '/Users/Uhuhu/Documents/Olympic Programing/Algorithms/C++/'

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
from FastOlympicCoding.run_options import run_options as _run_options
run_options = _run_options
