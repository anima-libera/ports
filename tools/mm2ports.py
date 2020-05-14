
""" Minsky Machine to Ports translator
This is a proof that Ports is Turing-complete !
"""

from ports import run_source
from generate_text import generate

REGISTER = """ ii{R}|o
{{
	m* o:pl|p{R} o:ml|m{R} o:0l|0{R} pl-lpl ml-lml vlp-frec vlm-0l e-1.1*. # init
	fp* lpl* vlp* lp* fp3-2.2*.
	fm* lml* vlm* fm1-3.3*.
	fb* vlp vlm-m{R} fp2-12.12*.
	frec* ii{R}|o{{}} ii{R}-4.4* lp-p{R} fr-0{R} fb-5.5*.
	fr* vlp-fb vlm-0l fm2-6.6*.
	fp2* fp-8.8*. fp3* fp-9.9*. # to fp
	fm1* fm-10.10*. fm2* fm-11.11*. # to fm
	e* # end
}}
"""
# If you want to understand how it works, get some paper and make some drawings to disassemble that shit
# Missign numbers are .. gone forever

def run_mm(mm):
	""" TODO """
	if "l" in mm["registers"]:
		raise Exception("no register named \"l\" u lil shit")
	registers = {}
	for register in mm["registers"]:
		registers[register] = 0
	code = {}
	for instr in mm["code"]:
		code[instr[0]] = instr
	ip = mm["code"][0][0]
	while True:
		if code[ip][1] == "+":
			registers[code[ip][2]] += 1
			ip = code[ip][3]
		elif code[ip][1] == "-":
			if registers[code[ip][2]] == 0:
				ip = code[ip][4]
			else:
				registers[code[ip][2]] -= 1
				ip = code[ip][3]
		elif code[ip][1] == "p":
			print(code[ip][2], end = "", flush = True)
			ip = code[ip][3]
		elif code[ip][1] == "h":
			break
		elif code[ip][1] == ".":
			ip = code[ip][3]
		else:
			raise Exception("whats dat shit \"{}\"".format(code[ip][1]))

def mm2ports(mm):
	""" TODO
	NOTE don't name the register "l" or it will not work ! """

	p = []
	i = 1

	p.append("m*")
	for register in mm["registers"]:
		p.append(REGISTER.format(R = register))
		p.append("ii{R}-x{i}.x{i}*\n".format(R = register, i = i))
		i += 1

	for instr in mm["code"]:
		p.append("{l}.{l}* ".format(l = instr[0])) # label
		if instr[1] == "+": # increment
			p.append("p{R}-x{i}.x{i}*".format(R = instr[2], i = i))
			i += 1
		elif instr[1] == "-": # decrement
			p.append("0{R}-{l}.m{R}-x{i}.x{i}*".format(R = instr[2], i = i, l = instr[4]))
			i += 1
		elif instr[1] == "p": # print
			code, i = generate(instr[2], start = i, pref = "x", readability = 0, new_i = True)
			p.append(code)
			p.append("of-x{i}.x{i}*".format(i = i))
			i += 1
		elif instr[1] == "h": # halt
			p.append("o-x{i}.x{i}*".format(i = i))
			i += 1
		elif instr[1] == ".": # nop (goto)
			pass
		else:
			raise Exception("whats dat shit \"{}\"".format(instr[1]))
		p.append("{l}-x{i}.x{i}*\n".format(i = i, l = instr[3])) # goto
		i += 1

	p.append("0-o.0*")
	return " ".join(p)

if __name__ == "__main__":

	def letsgo(mm):
		mm_ports = mm2ports(mm)
		print("\x1b[36m" + mm_ports + "\x1b[39m")
		print()
		print("\x1b[7mport version\x1b[27m")
		run_source(mm_ports)
		print()
		print("\x1b[7mpython 3 version\x1b[27m")
		run_mm(mm)
		print()

	mm_tuto = {
		"registers": ["a", "b"], # don't declare a register named "l" !
		"code":
		[
			[10, "+", "a",     20],     # label 10, increment "a" and goto 20
			[20, "-", "a",     30, 40], # label 20, decrement "b" and goto 30, but if "b" was 0 then goto 40 instead
			[30, "p", "hey\n", 40],     # label 30, print "hey\n" and goto 40
			[40, ".", 0,       50],     # label 40, goto 50
			[50, "h", 0, 0]             # label 50, halt
		]
	}

	mm_mult = {
		"registers": ["a", "b", "c", "e"],
		"code":
		[
			# a = 5; b = 3; c = 0; e = 0;
			[10, "+", "a", 20],
			[20, "+", "a", 30],
			[30, "+", "a", 40],
			[40, "+", "a", 60],
			[60, "+", "a", 200],
			[200, "+", "b", 210],
			[210, "+", "b", 220],
			[220, "+", "b", 300],

			# while (a > 0) { a--;
			[300, "-", "a", 400, 800],

			# c += b; e += b; b = 0;
			[400, "-", "b", 410, 600],
			[410, "+", "c", 420],
			[420, "+", "e", 400],

			# b += e; e = 0;
			[600, "-", "e", 610, 700],
			[610, "+", "b", 600],

			# }
			[700, ".", 0, 300],

			# while (c > 0) { c--;
			[800, "-", "c", 1000, 1200],

			# printf("o"); fflush(stdout); }
			[1000, "p", "o", 800],

			# printf("\n"); fflush(stdout); return;
			[1200, "p", "\n", 1210],
			[1210, "h", 0, 0],

			# it should have printed a*b times the "o"
		]
	}

	letsgo(mm_mult)

# TODO LIST
# TODO: make this script beautiful
# TODO: add a parser for https://esolangs.org/wiki/Portable_Minsky_Machine_Notation
