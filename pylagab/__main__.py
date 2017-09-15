import os.path
import sys

import tokenize

def main():
	if len(sys.argv) != 2:
		print('Usage: %s filename' % (os.path.basename(sys.argv[0])), file = sys.stderr)
		sys.exit(1)

	with open(sys.argv[1]) as f:
		text = f.read()

	tokenize.tokenize(text)

if __name__ == '__main__':
	main()
