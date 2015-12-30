import json


class CppDefConst(object):
	"""
	CppDefConst
	"""
	VARIABLE = 0
	METHOD = 1
	FUNCTION = 2
	TEMPLATE_DECLARE = 3
	LINE_COMMENT = 4
	MULTI_LINE_COMMENT_START = 5
	MULTI_LINE_COMMENT_END = 6
	FILE_END = 30



class CppParser(object):
	"""
	CppParser parse cpp and show completions
	"""
	class Parser(object):
		"""
		Parser parse simple code selections
		"""
		# def __init__(self):	
			# super(Parser, self).__init__()

		def is_word(s):
			return s == '_' or (ord('a') <= ord(s) <= ord('z') or ord('A') <= ord(s) <= ord('Z'))

		def get_seq(s, fpoint, checker=is_word):
			i = fpoint
			rez = ''
			while i < len(s) and checker(s[i]):
				rez += s
			return rez

		def next_token(s, point):
			i = point
			w = self.get_seq(s, point, checker=lambda x: return not x in {' ', '\n'})
			if not (i < len(s)):
				return CppDefConst.FILE_END
			if s[i] == '/':
				if i + 1 < len(s):
					if s[i + 1] == '/':
						return CppDefConst.LINE_COMMENT
					elif s[i + 1] == '*'
						return CppDefConst.MULTI_LINE_COMMENT_START
				else:
					return '/'
			elif is_word(s[i]):



			
	def __init__(self):
		super(CppParser, self).__init__()
		f = open('Default Types.JSON', 'r')
		d = json.loads(f.read())
		f.close()
		self.types = d
		self.empty_chars = {' ', '\n'}
		self.index = dict()
		self.code = ''

	def get_word_until(self, s, ind, begin_empty_chars=False):
		if begin_empty_chars:
			while ind < len(s) and s[ind] in self.empty_chars:
				ind += 1
		word = ''
		while ind < len(s) and self.is_word(s[ind]):
			word += s[ind]
			ind += 1
		return (word, ind)

	def next_token(self, s, point):
		i = point


	def parse_method(self, s):
		pass

	def parse_global(self, s):
		index = self.index
		types = self.types
		self.code = s
		empty_chars = self.empty_chars
		cnter = 0
		while cnter < len(s):
			if s[cnter] in empty_chars:
				cnter += 1
				continue
			word, cnter = self.get_word_until(s, cnter)
			if word == '#include':
				word, cnter = self.get_word_until(s, cnter)
				word = word.rstrip().lstrip()
				# *** need to parse word ***
			elif types.get(word, False):
				modificators = [types[word]]
				word, cnter = self.get_word_until(s, cnter, begin_empty_chars=True)
				while types.get(word, False):
					modificators.append(types[word])
					word, cnter = self.get_word_until(s, cnter, begin_empty_chars=True)
				print(modificators)
			else:
				cnter += 1


	def reparse_all(self, s):
		pass


cp = CppParser()
f = open('vector.cpp')

cp.parse_global(f.read())
f.close()