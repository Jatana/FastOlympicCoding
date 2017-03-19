# !restart sublime after change this file

run_options = [
	{
		'name': 'C++',
		'extensions': ['cpp'],
		'compile_cmd': '/usr/local/bin/g++-4.9 "{source_file}" -std=gnu++11',
		'run_cmd': './a.out -debug',

		'lint_compile_cmd': '/usr/local/bin/g++-4.9 -std=gnu++11 "{source_file}" -I "{source_file_dir}"'
	},

	{
		'name': 'Python',
		'extensions': ['py'],
		'compile_cmd': None,
		'run_cmd': '/Library/Frameworks/Python.framework/Versions/3.4/bin/python3 "{source_file}"'
	},
]