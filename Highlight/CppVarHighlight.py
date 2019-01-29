# Not Implemented

import re
from os import path


css = open(path.join(path.dirname(__file__), 'cpp_styles.css')).read()

DEF_TYPE = re.compile('int|float|double|char')
NUMBER = re.compile('\d+')
# STRING = re.compile('"\"')

class Token(object):
	"""docstring for Token"""
	def __init__(self, regex, css_class):
		self.regex = regex
		self.css_class = css_class


tokens = [
	Token(NUMBER, 'number'),
	Token(DEF_TYPE, 'def-type'),
]

def safety(s):
	return s.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>').replace(' ', '&nbsp;')


def highligh_regex(code, regex):
	code = regex.split(code)

def highlight(code):
	rez = '''
	<body style="margin: 0px; padding: 8px; background-color: var(--background); color: var(--foreground);">
	<style>
		%s
	</style>
	''' % css

	splited = NUMBER.split(code)
	nums = NUMBER.findall(code)
	spl3 = []

	for spl in splited:
		spl2 = DEF_TYPE.split(spl)
		nums2 = DEF_TYPE.findall(spl)
		nums2 = [('<div class="def-type">%s</div>' % num) for num in nums2]
		r = ""
		for i in range(len(spl2)):
			s = safety(spl2[i])
			if i < len(nums2):
				s += nums2[i]
			r += s
		spl3.append(r)
	splited = spl3

	nums = [('<div class="number">%s</div>' % num) for num in nums]
	for i in range(len(splited)):
		s = (splited[i])
		if i < len(nums):
			s += nums[i]
		rez += s

	rez += '</body>'
	# f = open(path.join(path.dirname(__file__), 'dbg.txt'), 'w')
	# print(rez, file=f)
	# f.close()
	return rez


def get_regions(code, pattern):
	match = pattern.search(code)
	regs = []
	dx = 0
	while match is not None:
		start, end = match.regs[0]
		regs.append((start + dx, end + dx))
		dx += end
		code = code[end:]
		match = pattern.search(code)
	return regs