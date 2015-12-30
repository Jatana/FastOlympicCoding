CLANG = 'Packages/C++/C++.tmLanguage'
PYTHON = 'Packages/Python/Python.tmLanguage'
PASCAL = 'Packages/Pascal/Pascal.tmLanguage'
OPDebugger = 'Packages/OP/OPDebugger.tmLanguage'


def get_syntax(view):
	return view.settings().get('syntax')