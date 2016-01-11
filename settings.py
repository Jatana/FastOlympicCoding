import sublime
from os import path
import os


plugin_name = 'SublimeFastOlympicCoding'
# root_dir = path.join(sublime.packages_path(), plugin_name + '/')
root_dir = path.split(__file__)[0]
if path.split(root_dir)[1] != plugin_name:
	os.rename(root_dir, path.join(path.split(root_dir)[0], plugin_name))

# print(root_dir)
