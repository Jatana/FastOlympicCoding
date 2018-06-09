import sublime
from os import path

base = path.dirname(__file__)

def get_test_styles(view):
	if view.settings().get('theme')	== 'Spacegray.sublime-theme':
		return open(path.join(base, 'test_styles_spacegray.css')).read()
	else:
		return open(path.join(base, 'test_styles.css')).read()