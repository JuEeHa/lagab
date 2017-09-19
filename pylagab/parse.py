from collections import namedtuple

from tokenize import token_types

Import_statement = namedtuple('Import_statement', 'imported')
Function_definition = namedtuple('Function_definition', ['name', 'arguments', 'return_types', 'body'])
Return_statement = namedtuple('Return_statement', 'expression')
Integer_literal = namedtuple('Integer_literal', 'value')
String_literal = namedtuple('String_literal', 'value')
Function_call = namedtuple('Function_call', ['name', 'arguments'])
Variable = namedtuple('Variable', 'name')
Let_statement = namedtuple('Let_statement', ['name', 'type', 'initializer'])

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
			raise ParsingError('Expected a token of type %s, got "%s" of type %s instead' % (token_type.name, token.contents, token.type.name))

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

	def identifier():
		name = [read_contents_type(token_types.identifier)]

		while not eol():
			# Look at what the next token is
			token_type, contents = peek_token()

			if token_type == token_types.symbol and contents == '.':
				# Dotted name. Remove the '.' from tokens to read and read the next part of the name
				read_token()
				name.append(read_contents_type(token_types.identifier))

			else:
				# Some kind of other token, we've read the whole identifier
				break

		return name

	def operatorless_expression():
		token_type, contents = peek_token()

		# Only allows literals or identifiers to start an operatorless expression
		if token_type not in (token_types.identifier, token_types.integer, token_types.string):
			raise ParsingError('Expected an identifier or a literal, got "%s" of type %s instead' % (contents, token_type.name))

		# If it's a literal, return the corresponding parse tree node type
		if token_type == token_types.integer:
			return Integer_literal(read_token().contents)

		elif token_type == token_types.string:
			return String_literal(read_token().contents)

		# For identifiers, figure out if it's a function call or a variable
		name = identifier()

		is_function_call = False
		if not eol():
			token_type, contents = peek_token()
			if token_type == token_types.symbol and contents == '(':
				is_function_call = True

		if is_function_call:
			# TODO: Implement support for multiple arguments
			match_token(token_types.symbol, '(')
			arguments = [expression()]
			match_token(token_types.symbol, ')')

			return Function_call(name, arguments)

		else:
			return Variable(name)

	def expression():
		# TODO: Implement precedence levels
		# TODO: Implement parentheses
		parsed = operatorless_expression()

		while not eol():
			token_type, contents = peek_token()

			if token_type == token_types.symbol and contents == ')':
				# End of this subexpression
				break

			operator = identifier()

			second_argument = operatorless_expression()

			parsed = Function_call(operator, (parsed, second_argument))

		return parsed

	def let_statement():
		match_token(token_types.identifier, 'let')

		variable_name = read_contents_type(token_types.identifier)

		match_token(token_types.symbol, ':')

		# TODO: Support more complex type expressions
		variable_type = read_contents_type(token_types.identifier)

		match_token(token_types.symbol, '=')

		initializer_expression = expression()

		return Let_statement(variable_name, variable_type, initializer_expression)

	def block():
		# TODO: Implement nested function definitions
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

			elif token_type == token_types.identifier and contents == 'let':
				# Let statement
				parsed.append(let_statement())

			else:
				# Expression
				parsed.append(expression())

			skip_newlines()

		return parsed

	def toplevel():
		parsed = []

		skip_possible_newlines()
		while not eof():
			token_type, contents = peek_token()

			if token_type != token_types.identifier:
				raise ParsingError('Expected a keyword, got %i instead' % token_type.name)

			if contents == 'import':
				# Import statement
				# Remove 'import' from tokens to read
				read_token()

				path = identifier()

				parsed.append(Import_statement(path))

			elif contents == 'fn':
				match_token(token_types.identifier, 'fn')

				name = read_contents_type(token_types.identifier)

				# TODO: Implement argument list parsing
				match_token(token_types.symbol, '(')
				skip_possible_newlines()
				match_token(token_types.symbol, ')')
				arguments = []

				# TODO: Parse multiple returns
				# TODO: Support more complex type expressions
				skip_possible_newlines()
				match_token(token_types.symbol, ':')
				return_types = [read_contents_type(token_types.identifier)]

				body = block()

				parsed.append(Function_definition(name, arguments, return_types, body))

			elif contents == 'let':
				# Let statement
				parsed.append(let_statement())

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
