
""" TODO
"""

def bytes2bits(b):
	l = []
	for byte in b:
		for i in range(8):
			l.append(int(bool(byte & (1 << (7-i))))) # int(bool( ... )) is such a beautiful function uwu
	return l

def bits2str(bits):
	return "".join([str(bit) for bit in bits])

def generate(text,
	start = 1, width = 3, o0_name = "o0", o1_name = "o1", readability = 1, comment_format = "# {c} = {b}\n", pref = "",
	new_i = False):
	""" Generate a bit of "Ports" code that append to the bit buffer the given 'text', utf-8 encoded.
	The port names used are numbers (with fixed 'width' if possible) starting with the 'start' parameter.
	The generated code can run if visible ports ('o0_name' and 'o1_name') are linked up to the special
	ports o0 and o1.
	The readability of the produced code can be influenced by the 'readability' parameter (dafault is 1):
	0: All the code in one line, no comments.
	1: One line per character, no comments.
	2: One line per bit, no comments.
	3: One line per character, with comments on the same line.
	4: Two lines per character, one for the comment, one for the code.
	5: Per character, one line comment and each bit on its own line.
	The comment text format can be changed with the 'comment_format' parameter.
	The 'pref' parameter add a prefix to each port instruction.
	The 'new_i' parameter add the i value to the result (see source code). """
	srccode = []
	i = start
	for c in text:
		bits = bytes2bits(bytes(c, encoding = "utf-8"))
		if readability in (4, 5):
			srccode.append(comment_format.format(c = repr(c), b = bits2str(bits)))
		for bit in bits:
			srccode.append("{}-{}{:0{w}d}.{}{:0{w}d}*".format(o0_name if bit == 0 else o1_name, pref, i, pref, i, w = width))
			i += 1
			if readability in (2, 5):
				srccode.append("\n")
		if readability == 3:
			srccode.append(comment_format.format(c = repr(c), b = bits2str(bits)))
		if readability in (1, 4):
			srccode.append("\n")
	if readability == 0:
		ret = "".join(srccode)
		return (ret, i) if new_i else ret
	else:
		ret = "".join(srccode[:-1])
		return (ret, i) if new_i else ret

if __name__ == "__main__":
	from sys import argv
	args = argv[1:]
	if len(args) == 0:
		print("usage:") 
		print("python3 {} <text> [start] [w] [o0] [o1] [readability] [comment]".format(argv[0]))
		print()
		print("Note that if <text> is an integer between 1 and 126 included, it is converted")
		print("to its ascii character, so that giving 10 gives the code for a '\\n' for ex.")
		exit(0)
	try:
		n = int(args[0])
		if 1 <= n <= 126:
			args[0] = chr(n) # see the usage message
	except:
		pass
	if len(args) == 1:
		print(generate(args[0]))
	elif len(args) == 2:
		print(generate(args[0], int(args[1])))
	elif len(args) == 3:
		print(generate(args[0], int(args[1]), int(args[2])))
	elif len(args) == 4:
		print(generate(args[0], int(args[1]), int(args[2]), args[3]))
	elif len(args) == 5:
		print(generate(args[0], int(args[1]), int(args[2]), args[3], args[4]))
	elif len(args) == 6:
		print(generate(args[0], int(args[1]), int(args[2]), args[3], args[4], int(args[5])))
	elif len(args) == 7:
		print(generate(args[0], int(args[1]), int(args[2]), args[3], args[4], int(args[5]), args[6]))
	elif len(args) == 8:
		print(generate(args[0], int(args[1]), int(args[2]), args[3], args[4], int(args[5]), args[6], args[7]))
	# It may be more confortable to import the generate function in the python REPL
