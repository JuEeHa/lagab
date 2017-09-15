import enum
from collections import namedtuple

class token_types(enum.Enum):
	integer, string, symbol, identifier = range(4)

Token = namedtuple('Token', ['type', 'contents'])

class TokenizationError(Exception): None

symbols = {':', '.', '{', '}', '[', ']', '(', ')'}

def is_digit(char, base = 10):
	# We only suppor bases 10 and 16
	assert base == 10 or base == 16

	if base == 10:
		# For base 10, .isnumeric() works
		return char.isnumeric()

	elif base == 16:
		# allow a-f and A-F as well
		return char.isnumeric() or ord('a') <= ord(char) <= ord('f') or ord('A') <= ord(char) <= ord('F')

def can_continue_symbol(char, symbol = ''):
	possible_symbol = symbol + char
	length = len(possible_symbol)
	for symbol in symbols:
		# Check possible symbol against pefixes of symbols
		if symbol[:length] == possible_symbol:
			return True

	# No matching prefixes
	return False

def is_identifier(char):
	return not char.isspace() and not can_continue_symbol(char) and not char in ('"', "'")

def tokenize_line(line):
	def eol():
		nonlocal line, index
		return index >= len(line)

	def peek_char():
		nonlocal line, index

		assert not eol()

		return line[index]

	def read_char():
		nonlocal line, index
		
		assert not eol()

		char = line[index]

		index += 1

		return char

	def skip_whitespace():
		nonlocal line, index

		while not eol() and line[index].isspace():
			index += 1

	def read_integer():
		# Read first character
		string = read_char()

		# See if we have a non-base10 number
		base = 10
		if string == '0' and not eol():
			if peek_char() == 'x':
				base = 16
				# Remove the 'x' from the input stream and remove the '0' from the number
				# This is because '0x' is the prefix, and not part of the number itself
				read_char()
				string = ''

		# Read all digits
		while not eol() and is_digit(peek_char(), base = base):
			string += read_char()

		return int(string, base)

	def read_string():
		quote = read_char()
		string = ''
		
		while True:
			if eol():
				# End of line encountered before matching quote found
				raise TokenizationError('Unmatched quote')

			# Only terminate on matching quote
			if peek_char() == quote:
				# Remove the quote from the chars to read
				read_char()

				# Is next character same quote again?
				if not eol() and peek_char() == quote:
					# Yes, add the quote to string, remove it from input and continue reading
					string += quote
					read_char()

				else:
					# No, break out of the loop
					break

			string += read_char()

		return string

	def read_symbol():
		string = read_char()

		while not eol() and can_continue_symbol(peek_char(), symbol = string):
			string += read_char()

		return string

	def read_identifier():
		string = read_char()

		while not eol() and is_identifier(peek_char()):
			string += read_char()

		return string

	index = 0
	tokens = []

	skip_whitespace()
	while not eol():
		current_char = peek_char()
		if current_char == '#':
			# We found a comment, ignore rest of line
			break

		if current_char.isnumeric():
			# Integer literal
			token_type = token_types.integer
			contents = read_integer()

		elif current_char in ('"', "'"):
			# String
			token_type = token_types.string
			contents = read_string()

		elif can_continue_symbol(current_char):
			# Symbol
			token_type = token_types.symbol
			contents = read_symbol()

		else:
			# Identifier or a keyword
			token_type = token_types.identifier
			contents = read_identifier()

		tokens.append(Token(type = token_type, contents = contents))

		# Skip until either end of line or to start of the next token
		skip_whitespace()

	return tokens

def tokenize(text):
	tokenized_lines = []

	for line_number, line in enumerate(text.split('\n')):
		try:
			tokenized_line = tokenize_line(line)

		except TokenizationError as err:
			assert len(err.args) == 1
			print('%i: Tokenization Error: %s' % (line_number, err.args[0]))
			raise err

		else:
			print(line_number)
			for token in tokenized_line:
				print('\t%s: %s' % (token.type.name, token.contents))

			tokenized_lines.append(tokenized_line)

	return tokenized_lines
