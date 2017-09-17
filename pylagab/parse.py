from collections import namedtuple

from tokenize import token_types

Import_statement = namedtuple('Import_statement', 'imported')
Function_definition = namedtuple('Function_definition', ['name', 'arguments', 'return_types', 'body'])
Return_statement = namedtuple('Return_statement', 'expression')

class ParsingError(Exception): None

def parse(tokenized_lines):
	def eof():
		nonlocal tokenized_lines, line_number

		return line_number >= len(tokenized_lines)

	def eol():
		nonlocal tokenized_lines, line_number, index

		assert not eof()

		return index >= len(tokenized_lines[line_number])

	def peek_token():
		nonlocal tokenized_lines, line_number, index

		if eof():
			raise ParsingError('Unexpected end of file')
		if eol():
			raise ParsingError('Unexpected end of line')

		return tokenized_lines[line_number][index]

	def read_token():
		nonlocal index

		token = peek_token()

		index += 1

		return token

	def read_contents_type(token_type):
		"""Only read a token of the type passed, otherwise throw error"""
		if eof():
			raise ParsingError('Unexpected end of file, expected a token of type %s' % token_type.name)
		if eol():
			raise ParsingError('Unexpected end of line, expected a token of type %s' % token_type.name)

		token = read_token()
		if token.type != token_type:
			raise ParsingError('Expected a token of type %s, got %s instead' % (token_type.name, token.type.name))

		return token.contents

	def match_token(token_type, contents):
		"""Match against token in the stream, throw error if unsuccesful"""
		if eof():
			raise ParsingError('Unexpected end of file, expected a token "%s" of type %s' % (contents, token_type.name))
		if eol():
			raise ParsingError('Unexpected end of line, expected a token "%s" of type %s' % (contents, token_type.name))

		token = read_token()
		if token.type != token_type or token.contents != contents:
			raise ParsingError('Expected a token "%s" of type %s, got "%s" of type %s instead' % (contents, token_type.name, token.contents, token.type.name))

	def next_line():
		nonlocal line_number, index

		assert not eof()
		assert eol()

		line_number += 1
		index = 0

	def skip_possible_newlines():
		while not eof() and eol():
			next_line()

	def skip_newlines():
		if not eol():
			token_type, contents = read_token()
			raise ParsingError('Expected end of line, got "%s" of type %s instead' % (contents, token_type))

		while not eof() and eol():
			next_line()

	def expression():
		# TODO: Implement expression parsing
		while not eol():
			read_token()
		return None

	def block():
		skip_possible_newlines()
		match_token(token_types.symbol, '{')

		parsed = []

		skip_possible_newlines()
		while True:
			token_type, contents = peek_token()

			if eof():
				raise ParsingError('Unexpected end of file, expected "}"')

			elif token_type == token_types.symbol and contents == '}':
				# End of block
				# This is because toplevel() expectes the pointers to be left at an end of line, or it will complain about junk
				read_token()
				break

			elif token_type == token_types.identifier and contents == 'ret':
				# Return statement
				# Remove 'ret' from tokens to read
				read_token()

				returned = expression()
				parsed.append(Return_statement(returned))

			else:
				# Expression
				parsed.append(expression())

			skip_newlines()

		return parsed

	def toplevel():
		parsed = []

		skip_possible_newlines()
		while not eof():
			token_type, contents = read_token()

			if token_type != token_types.identifier:
				raise ParsingError('Expected a keyword, got %i instead' % token_type.name)

			if contents == 'import':
				# Import statement
				path = []
				path.append(read_contents_type(token_types.identifier))
				while not eol():
					match_token(token_types.symbol, '.')
					path.append(read_contents_type(token_types.identifier))

				parsed.append(Import_statement(path))

			elif contents == 'fn':
				name = read_contents_type(token_types.identifier)

				# TODO: Implement argument list parsing
				match_token(token_types.symbol, '(')
				skip_possible_newlines()
				match_token(token_types.symbol, ')')
				arguments = []

				# TODO: Parse multiple returns
				skip_possible_newlines()
				match_token(token_types.symbol, ':')
				return_types = read_contents_type(token_types.identifier)

				body = block()

				parsed.append(Function_definition(name, arguments, return_types, body))

			else:
				raise ParsingError('Unknown keyword: %s' % contents)

			skip_newlines()

		return parsed


	line_number = 0
	index = 0

	try:
		parsed = toplevel()

	except ParsingError as err:
		# Have line number displayed as 1-indexed, even if it is internally 0-indexed
		print('%i: Parsing Error: %s' % (line_number + 1, err.args[0]))
		raise err

	else:
		return parsed
