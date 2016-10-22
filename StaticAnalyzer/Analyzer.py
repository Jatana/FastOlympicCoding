# Not Implemented

import re


class ClassInfo(object):
	"""
	contains members of class
	"""
	def __init__(self, name, template=None):
		self.name = name
		self.template = template

	def is_struct(self):
		pass

	def template(self):
		pass

class NameSpaceInfo(object):
	"""docstring for NameSpaceInfo"""
	def __init__(self):
		pass
	
class FunctionInfo(object):
	"""docstring for FunctionInfo"""
	def __init__(self):
		pass

class VarInfo(object):
	"""docstring for VarInfo"""
	def __init__(self):
		pass

class TemplateInfo(object):
	"""docstring for TemplateInfo"""
	def __init__(self, args):
		self.args = args

	def __str__(self):
		return '<' + ', '.join(self.args) + '>'

class Token(object):
	"""docstring for token"""
	def __init__(self, t_type, str_token=None):
		self.t_type = t_type
		self.str_token = str_token

	def is_bracket(self):
		s = self.str_token
		return s in '<>()[]{}'

	def is_open_bracket(self):
		return self.str_token in '<({['

	def __str__(self):
		return "<%s, `%s`>" % (self.t_type, self.str_token)

	def __eq__(self, obj):
		if type(obj) == str:
			return self.str_token == obj
		return self == obj
		
class TokenType:
	"""docstring for TokenType"""
	OPERATOR = 'OPERATOR'
	WHITESPACE = 'WHITESPACE'
	BRACKET = 'BRACKET'
	WORD = 'WORD'
	ACCESS_OPERATOR = 'ACCESS_OPERATOR'
	UNKNOWN = 'UNKNOWN'
	END_COMMAND = 'END_COMMAND'
	STRING = 'STRING'
	CHAR = 'CHAR'
	NUMBER = 'NUMBER'

class IndexError(Exception):
	"""docstring for IndexError"""
	def __init__(self, token_ind, err_msg=''):
		self.token_ind = token_ind
		self.err_msg = err_msg

	def __str__(self):
		return 'Error While Indexing %d, err_msg: %s' % (token_ind, self.err_msg)


class CppAnalyzer(object):
	"""
	CppAnalyzer
	Module to Index Preprocessed Cpp Code
	>INDEV!
	"""

	DEFAULT_TYPES = [
		ClassInfo(x) for x in ['int','float','double','unsigned','signed','char','long','bool']
	]

	BRACKET_PAIR = {
		'{':'}', '}':'{', '[':']', ']':'[', '(':')', ')':'(', '<':'>', '>':'<'
	}

	class TokenSpliter(object):
		"""docstring for TokenSpliter"""
		def __init__(self, code):
			super(TokenSpliter, self).__init__()
			self.code = code
			
		def __init__(self, code):
			self.code = code		

		def is_var_char(self, ind):
			c = self.code[ind]
			return c.isalpha() or c == '_' or c.isdigit()

		def is_operator_char(self, ind):
			c = self.code[ind]
			return c in '<>&^=-+/|%*'

		def is_whitespace(self, ind):
			return self.code[ind] in '\n\t '

		def is_bracket(self, ind):
			return self.code[ind] in '[](){}'

		def is_access_operator(self, ind):
			return self.code[ind:ind + 2] in {'::', '->'} or self.code[ind] == '.'

		def end_of(self, beg, f):
			code = self.code
			while beg < len(code) and f(beg):
				beg += 1
			return beg

		def end_word(self, beg):
			return self.end_of(beg, self.is_var_char)

		def end_operator(self, beg):
			return self.end_of(beg, self.is_operator_char)

		def end_access_operator(self, beg):
			code = self.code
			if code[beg:beg + 2] in {'->', '::'}:
				return beg + 2
			return beg + 1

		def end_whitespace(self, beg):
			return self.end_of(beg, self.is_whitespace)

		def end_number(self, beg):
			code = self.code
			return self.end_of(beg, lambda ind: code[ind].isdigit() or code[ind].isalpha())

		def end_string(self, beg):
			'''
			beg contains begin of string
			"asd"
			^    ^
			'''
			code = self.code
			beg += 1
			while beg < len(code) and code[beg] != '"':
				if code[beg] == '\\':
					beg += 1
				beg += 1
			return beg + 1

		def end_char(self, beg):
			"""
			end of char
			'\t'
			^___^
			"""
			code = self.code
			beg += 1
			while beg < len(code) and code[beg] != "'":
				if code[beg] == '\\':
					beg += 1
				beg += 1
			return beg + 1

		def split(self):
			code = self.code
			it = 0
			tokens = []
			while it < len(code):
				# Detect WhiteSpace
				if self.is_whitespace(it):
					it = self.end_whitespace(it)
					# tokens.append(Token(TokenType.WHITESPACE))
				# detect Digit
				elif code[it].isdigit():
					end = self.end_number(it)
					tokens.append(Token(TokenType.NUMBER, code[it:end]))
					it = end

				# Detect Word
				elif self.is_var_char(it):
					end = self.end_word(it)
					tokens.append(Token(TokenType.WORD, str_token=code[it:end]))
					it = end
				# Detect String
				elif code[it] == '"':
					end = self.end_string(it)
					tokens.append(Token(TokenType.STRING, str_token=code[it + 1:end - 1]))
					it = end
				#Detext Char
				elif code[it] == "'":
					end = self.end_char(it)
					tokens.append(Token(TokenType.CHAR, str_token=code[it + 1:end - 1]))
					it = end
				# Detect Bracket
				elif self.is_bracket(it):
					tokens.append(Token(TokenType.BRACKET, str_token=code[it]))
					it += 1
				# Specail Detect for `<` and `>`
				elif code[it] in {'<', '>'}:
					tokens.append(Token(TokenType.OPERATOR, str_token=code[it]))
					it += 1
				# Detect Operator
				elif self.is_operator_char(it):
					end = self.end_operator(it)
					tokens.append(Token(TokenType.OPERATOR, str_token=code[it:end]))
					it = end
				# Detect Access operators
				elif self.is_access_operator(it):
					end = self.end_access_operator(it)
					tokens.append(Token(TokenType.ACCESS_OPERATOR, str_token=code[it:end]))
					it = end
				# Detect `:`
				elif self.code[it] == ':':
					tokens.append(Token(TokenType.UNKNOWN, str_token=code[it]))
					it += 1
				# Detect command end;
				elif self.code[it] == ';':
					if len(tokens) == 0 or tokens[-1].t_type != TokenType.END_COMMAND:
						tokens.append(Token(TokenType.END_COMMAND))
					it += 1
				else:
					tokens.append(Token(TokenType.UNKNOWN, str_token=code[it]))
					it += 1

			return tokens

	def __init__(self, code):
		self.code = code

	def find_bracket_pair(self, ind, shift=1):
		tokens = self.tokens
		bracket = tokens[ind].str_token
		pair_bracket = self.BRACKET_PAIR[bracket]
		it = ind + shift
		bal = 1
		while 0 <= it < len(tokens) and bal != 0:
			# print(bal, pair_bracket, tokens[it].str_token)
			if tokens[it].t_type in {TokenType.BRACKET, TokenType.OPERATOR} and \
				tokens[it].str_token in {bracket, pair_bracket}:
				if tokens[it].str_token == bracket:
					bal += 1
				elif tokens[it].str_token == pair_bracket:
					bal -= 1
			if bal == 0:
				break
			it += shift
		# print(tokens[it].__str__())
		return it

	def merge_tokens(self, tokens):
		if not tokens:
			return ''
		s = tokens[0].str_token
		for i in range(len(tokens) - 1):
			t1 = tokens[i].t_type
			t2 = tokens[i + 1].t_type
			need_sep = False
			if t1 == TokenType.WORD and t2 == TokenType.WORD:
				need_sep = True
			elif (tokens[i].str_token, tokens[i + 1].str_token) in {('<', '>'), ('>', '<')}:
				need_sep = False
			if need_sep:
				s += ' '
			s += tokens[i + 1].str_token
		return s



	def split_args(self, begin, end, ignore_brackets='[({<'):
		'''
		splits args
		<int, vector<int>>
		^			end-> ^
		'''
		tokens = self.tokens
		split_pos = []
		i = begin + 1
		bal = 0
		while i < end:
			if tokens[i] == ',':
				if bal == 0:
					split_pos.append(i)
			elif tokens[i].is_bracket():
				if tokens[i].is_open_bracket():
					bal += 1
				else:
					bal -= 1
			i += 1
		return split_pos



	def index_template(self, it):
		'''
		index template. takes pointer to word template
		return indexed template and end of template
		'''
		tokens = self.tokens
		if tokens[it + 1].str_token != '<':
			return IndexError(it + 1, err_msg='waiting for template')
		end = self.find_bracket_pair(it + 1)
		split_pos = [it + 1] + self.split_args(it + 1, end + 1) + [end]
		args = []
		for i in range(len(split_pos) - 1):
			args.append(self.merge_tokens(tokens[split_pos[i] + 1:split_pos[i + 1]]))
		print(args)
		return TemplateInfo(args), end + 1

	def __index(self, it, cur_scope):
		pass

	def index(self):
		code = self.code
		ts = CppAnalyzer.TokenSpliter(code)
		tokens = ts.split()
		self.tokens = tokens
		for i in range(len(tokens)):
			print(tokens[i].__str__(), i)
		# print(self.split_args(0, self.find_bracket_pair(0) + 1))
		self.index_vis = dict()
		self.__index(0, self.index_vis)



# code = open('/users/uhuhu/tmp/out.txt').read()
___code = open('kekus.cpp').read()
# code = clean(code)
analyzer = CppAnalyzer(___code)
analyzer.index()
# tokens = analyzer.split_by_tokens()
# for token in tokens:
	# print(token.__str__())