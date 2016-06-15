from os import path

CLANG = 'Packages/C++/C++.tmLanguage'
PYTHON = 'Packages/Python/Python.tmLanguage'
PASCAL = 'Packages/Pascal/Pascal.tmLanguage'
OPDebugger = 'Packages/OP/OPDebugger.tmLanguage'


def get_syntax(view):
	return view.settings().get('syntax')

def is_cpp_file(view):
	try:
		f = view.file_name()
		return path.splitext(f)[1][1:] in {'cpp'}
	except:
		return False


def is_python_file(view):
	try:
		f = view.file_name()
		return path.splitext(f)[1][1:] in {'py'}
	except:
		return False
