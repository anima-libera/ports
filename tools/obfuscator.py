
""" TODO
Please note that this is clearly unoptimized because who cares
"""

import re
from random import choice

SPECIAL_NAMES = ["o", "o0", "o1", "of", "os", "sa", "ia", "ir"]
NAME_CHARS = "".join([chr(n) for n in range(ord("a"), ord("z")+1)]+[str(i) for i in range(10)])
generated_names = {}

def _generate_name(n):
	""" see generate_name """
	return "".join([choice(NAME_CHARS) for i in range(n)])

def generate_name(base):
	""" generate a new random non-special name if necessary """
	global generated_names
	if base in SPECIAL_NAMES:
		return base
	if base in generated_names.keys():
		return generated_names[base]
	n = 1
	name = _generate_name(n)
	while (name in generated_names.values()) or (name in SPECIAL_NAMES):
		n += 1
		name = _generate_name(n)
	generated_names[base] = name
	return name

def _isnamechar(c):
	""" TODO """
	return ord("a") <= ord(c) <= ord("z") or ord("0") <= ord(c) <= ord("9")

def obfuscate(src, c80max = False, iterations = 1):
	""" TODO """
	if not src:
		return ""
	def replace_name(match):
		return generate_name(match.group(0))
	parts = (re.sub(r"([a-z0-9]+)", replace_name, src)).split()
	patrsj = []
	for i in range(len(parts)-1):
		patrsj.append(parts[i])
		if _isnamechar(parts[i][0]) and _isnamechar(parts[i+1][0]):
			patrsj.append(".")
	patrsj.append(parts[-1])
	osrc = "".join(parts)
	if c80max:
		p = []
		l = 0
		i = 78
		while i < len(osrc)-1:
			while _isnamechar(osrc[i]) and _isnamechar(osrc[i+1]):
				i -=  1
			p.append(osrc[l:i+1])
			l = i+1
			i += 79
		p.append(osrc[l:i+1])
		osrc = "\n".join(p)
	if iterations > 1: # o god this is shit
		other = obfuscate(src, c80max = c80max, iterations = iterations-1)
		if len(other) < len(osrc):
			osrc = other
	return osrc

if __name__ == "__main__":
	from sys import argv, stdin
	c80max = ("-8" in argv)
	opt = ("-o" in argv) # dont do that
	if "-p" in argv:
		print(obfuscate(stdin.read(), c80max = c80max, iterations = 200 if opt else 1))
	else:
		print(obfuscate(argv[1], c80max = c80max, iterations = 200 if opt else 1))
