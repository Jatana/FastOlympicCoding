import sublime
from os import path

plugin_name = 'FastOlympicCoding'
root_dir = path.split(__file__)[0]

settings_file = 'CppFastOlympicCoding ({os}).sublime-settings'.format(
	os={ 'windows': 'Windows', 'linux': 'Linux', 'osx': 'OSX' }[sublime.platform().lower()]
)

settings = {}

def get_settings():
	return settings

def load_settings():
	global settings
	_settings = sublime.load_settings(settings_file)
	if _settings is None:
		sublime.set_timeout_async(load_settings, 200)
	else:
		settings = _settings
		sublime.status_message('CppFastOlympicCoding: settings loaded')

def plugin_loaded():
	sublime.set_timeout(load_settings, 200)
