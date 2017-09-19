import os.path
import sys

import tokenize
import parse
import gen_ir

def main():
	if len(sys.argv) != 2:
		print('Usage: %s filename' % (os.path.basename(sys.argv[0])), file = sys.stderr)
		sys.exit(1)

	with open(sys.argv[1]) as f:
		text = f.read()

	try:
		tokenized = tokenize.tokenize(text)

	except tokenize.TokenizationError:
		sys.exit(1)

	try:
		parsed = parse.parse(tokenized)

	except parse.ParsingError:
		sys.exit(1)

	parse.prettyprint_parsed(parsed)
	print()

	ir = gen_ir.gen_ir(parsed)

	gen_ir.prettyprint_ir(ir)

if __name__ == '__main__':
	main()
