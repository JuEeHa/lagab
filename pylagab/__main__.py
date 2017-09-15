import os.path
import sys

import tokenize

def main():
	if len(sys.argv) != 2:
		print('Usage: %s filename' % (os.path.basename(sys.argv[0])), file = sys.stderr)
		sys.exit(1)

	with open(sys.argv[1]) as f:
		text = f.read()

	try:
		tokenize.tokenize(text)
	except tokenize.TokenizationError:
		sys.exit(1)

if __name__ == '__main__':
	main()
