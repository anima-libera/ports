
""" TODO
"""

# Please note that this is a reference implementation of an esoteric language (I designed)
# thus the code and the comments that follow this comment are informal.
# This disclamer has been written in case I ever use this file in a professional portfolio
# that was supposed to contain only serious work.
# Despite the comments, the code and the project itself are serious to me though.

# Please note that when I code in C I try not to write past the 80 characters holy barrier
# but when I code in python the only barrier I respect is my screen's width, thus I am not
# sorry if the code doesn't display nicely on whatever you are using to read this, in such
# a case just zoom out a little, believe me you'll recover from this.

# Please note also that I like to write a comment about a line or a group of lines after this
# line or this group of lines, and this is fine.

#### Header and miscellaneous

__author__ = "Anima Libera <anim.libera@gmail.com>"
__copyright__ = "Public Domain"
__version__ = "0.4" # TODO set to 1.0 once it works

from sys import version_info as _version_info
if _version_info.major < 3 or _version_info.minor < 6:
	raise Exception("python version above or equal to 3.6 is required")
	# because the 'encoding' kwarg of subprocess.run is used and is a 3.6 python feature

import subprocess as _subprocess
from enum import Enum as _Enum

class PortslangEnum(_Enum):
	""" TODO """

	def __repr__(self):
		return "{}.{}".format(self.__class__.__name__, self.name)
		# In theory eval(repr(x)) == x

	def lowercase_name(self):
		""" TODO """
		return str(self.name).lower()

class PortslangException(Exception):
	""" TODO """

class PortslangBug(PortslangException):
	""" TODO """

#### Color section

# See https://en.wikipedia.org/wiki/ANSI_escape_code for more info about this section.
# Running this script with the flag --no-ansi-codes turns _ansi_codes_enabled to False
# before anything is printed.
# All of this has been done so that _print_dbg can look even better with colors.

_ansi_codes_enabled = True
_color_stack = []
_RED = 31
_GREEN = 32
_YELLOW = 33
_BLUE = 34
_MAGENTA = 35
_CYAN = 36
_NEGATIVE = -1 # not really an ansi color code 
_DEFAULT = None # not an ansi color code at all

def _set_color(color_code):
	""" TODO
	- The color code _DEFAULT represents the default fg color.
	- The color code _NEGATIVE represents the negative (reverse fg and bg) effect.
	- For other color codes, see https://en.wikipedia.org/wiki/ANSI_escape_code. """
	global _ansi_codes_enabled
	if _ansi_codes_enabled:
		if color_code == _DEFAULT:
			print("\x1b[27m\x1b[39m", end = "") # no negative, default fg color
		elif color_code == _NEGATIVE:
			print("\x1b[39m\x1b[7m", end = "") # default fg color, negative
		else:
			print("\x1b[27m\x1b[{}m".format(color_code), end = "") # no negative, given fg color

def _push_color(color_code):
	""" TODO """
	global _color_stack
	_color_stack.append(color_code)
	_set_color(color_code)

def _pop_color():
	""" TODO """
	global _color_stack
	_color_stack.pop()
	if _color_stack:
		_set_color(_color_stack[-1])
	else:
		_set_color(None)

#### Debug section

# Running this script with the flag --debug or -d turns _debug_enabled to True
# before anything is done.

_debug_enabled = False
_print_dbg_level = 0

class _LvlDiff(PortslangEnum):
	""" TODO """
	BEG = 1
	END = 2
	NO = 3

def _print_dbg_line(lvldiff, firstline, lastline, line, color = None, **kwargs):
	""" TODO
	Sould be called only by _print_dbg because it doesn't check _debug_enabled. """
	global _print_dbg_level
	_push_color(None)
	if lvldiff == _LvlDiff.BEG and firstline:
		if _print_dbg_level < 0:
			_print_dbg_level = 0
		print("│" * _print_dbg_level, end = "")
		_print_dbg_level += 1
		print("┌", end = "")
	elif lvldiff == _LvlDiff.END and lastline:
		_print_dbg_level -= 1
		if _print_dbg_level < 0:
			_print_dbg_level = 0
		print("│" * _print_dbg_level, end = "")
		print("└", end = "")
	else:
		if _print_dbg_level < 0:
			_print_dbg_level = 0
		print("│" * _print_dbg_level, end = "")
	_pop_color()
	_push_color(color)
	print(line, **kwargs) # here it is
	_pop_color()
	# do I spend too much time on details ? ye

def _print_dbg(lvldiff, text, color = None, **kwargs):
	""" TODO
	The text parameter can be a string or an object of a class that has a _print_dbg method. """
	global _debug_enabled
	if _debug_enabled:
		if hasattr(text, "_print_dbg") and callable(text._print_dbg):
			text._print_dbg()
		else:
			lines = text.split("\n")
			if not lines:
				lines = ["\n"]
			for i, line in enumerate(lines):
				_print_dbg_line(lvldiff, i == 0, i == len(lines)-1, line, color = color, **kwargs)

def _bug(exception):
	""" TODO """
	_print_dbg(_LvlDiff.NO, str(exception), color = _RED)
	raise exception

def _error(exception):
	""" TODO """
	# Is this exactly the same code as in the _bug function ?
	_print_dbg(_LvlDiff.NO, str(exception), color = _RED)
	raise exception

#### Parser section

# The _parse_new_token's doc string is a good start to have a quick look at this parser.
# Every thing here was written to make the parse and parse_file functions.
# Having a look at the Ports esoteric programming language documentation may help.

class PortslangParsingException(PortslangException):
	""" TODO """

class UnexpectedCharacterError(PortslangParsingException):
	""" TODO """

	def __init__(self, character, loc):
		self.character = character
		self.loc = loc
		super().__init__("unexpected character {} (codepoint {}) at loc {}".format(
			repr(character), ord(character), str(loc)))

class UnexpectedTokenTypeError(PortslangParsingException):
	""" TODO """

	def __init__(self, token, situation):
		self.token = token
		self.situation = situation
		self.loc = token.loc
		super().__init__("unexpected {} token {} at loc {}".format(token.lowercase_type(), situation, self.loc))

class Loc:
	""" TODO """

	def __init__(self, i, line, filename):
		self.i = i
		self.line = line
		self.filename = filename

	def __repr__(self):
		return "Loc({}, {}, {})".format(self.i, self.line, repr(self.filename))
		# I'm a fan of the eval(repr(x)) == x thing

	def __str__(self):
		return "{} line {}{}".format(self.i, self.line, " in {}".format(self.filename) if self.filename else "")

class _TokenType(PortslangEnum):
	""" TODO """
	NAME = 1 # data is a string
	OP = 2 # data is one of "*", "-", "/", ":", "|"
	NOP = 3 # data is a _TokenNopSubtype
	CODE = 4 # data is a Code

class _TokenNopSubtype(PortslangEnum):
	""" TODO """
	INSTR = 1 # nop instruction "."
	EOSC = 2 # end of subcode "}"
	EOF = 3 # end of file EOF

	def lowercase_pretty_name(self):
		""" TODO """
		if self == _TokenNopSubtype.INSTR:
			return "nop"
		elif self == _TokenNopSubtype.EOSC:
			return "end-of-subcode"
		elif self == _TokenNopSubtype.EOF:
			return "end-of-file"
		else:
			_bug(PortslangBug("bug in _TokenNopSubtype.lowercase_pretty_name: unkown value"))

class _Token:
	""" TODO
	Token is an internal class because it is not supposed to show up to a user ; 
	the parse function produces a Code object, the _Token class is only used by internal functions. """

	def __init__(self, type, data, loc):
		self.type = type
		self.data = data # can be a string, a Code or a _TokenNopSubtype
		self.loc = loc

	def __repr__(self):
		return "_Token({}, {}, {})".format(repr(self.type), repr(self.data), repr(self.loc))
		# In theory eval(repr(token)) == token

	def lowercase_type(self):
		""" TODO """
		if self.type == _TokenType.NOP:
			return self.data.lowercase_pretty_name()
		else:
			return self.type.lowercase_name()

def _tl_append(tl, token):
	""" TODO """
	tl.append(token)
	if token.type == _TokenType.NAME:
		_print_dbg(_LvlDiff.NO, "name \"{}\" added to tl".format(token.data))
	elif token.type == _TokenType.OP:
		_print_dbg(_LvlDiff.NO, "op \"{}\" added to tl".format(token.data))
	elif token.type == _TokenType.NOP:
		_print_dbg(_LvlDiff.NO, "nop added to tl")
	elif token.type == _TokenType.CODE:
		_print_dbg(_LvlDiff.NO, "code added to tl")
	else:
		_bug(PortslangBug("bug in _tl_append: unkown token type"))
		# this is unnecessary but **** ***

def _tl_clear(tl):
	""" TODO """
	tl.clear()
	_print_dbg(_LvlDiff.NO, "tl cleared")

def _parse_new_token_0(tl, code, token):
	""" TODO
	Assume that len(tl) == 0. """
	if token.type == _TokenType.NAME:
		_tl_append(tl, token)
	elif token.type == _TokenType.NOP:
		_print_dbg(_LvlDiff.NO, "{} discarded".format(token.data.lowercase_pretty_name()))
		if code.isempty() and token.data == _TokenNopSubtype.INSTR:
			code.empty = False
			_print_dbg(_LvlDiff.NO, "code not empty")
	else:
		_error(UnexpectedTokenTypeError(token, "(expected a name, a nop, an end-of-subcode or an end-of-file)"))

def _parse_new_token_1(tl, code, token):
	""" TODO
	Assume that len(tl) == 1 and that tl[0] is a name. """
	if token.type == _TokenType.NAME:
		_print_dbg(_LvlDiff.NO, "cut-link \"{}\"".format(tl[0].data), color = _NEGATIVE)
		code.append(InstructionCutlink(tl[0].data, tl[0].loc))
		_tl_clear(tl)
		_tl_append(tl, token)
	elif token.type == _TokenType.NOP:
		_print_dbg(_LvlDiff.NO, "cut-link \"{}\"".format(tl[0].data), color = _NEGATIVE)
		code.append(InstructionCutlink(tl[0].data, tl[0].loc))
		_tl_clear(tl)
	elif token.data == "*":
		_print_dbg(_LvlDiff.NO, "port \"{}\" *".format(tl[0].data), color = _NEGATIVE)
		code.append(InstructionPort(tl[0].data, tl[0].loc))
		_tl_clear(tl)
	elif token.type == _TokenType.OP:
		_tl_append(tl, token)
	else:
		_error(UnexpectedTokenTypeError(token, "after a name"))

def _parse_new_token_2(tl, code, token):
	""" TODO
	Assume that len(tl) == 2, that tl[0] is a name and tl[1] is a non-"*" op. """
	if token.type == _TokenType.NAME:
		if tl[1].data == "-":
			_print_dbg(_LvlDiff.NO, "create-link \"{}\" - \"{}\"".format(tl[0].data, token.data), color = _NEGATIVE)
			code.append(InstructionCreatelink(tl[0].data, token.data, tl[0].loc))
			_tl_clear(tl)
		elif tl[1].data == "/":
			_print_dbg(_LvlDiff.NO, "swap-link \"{}\" / \"{}\"".format(tl[0].data, token.data), color = _NEGATIVE)
			code.append(InstructionSwaplink(tl[0].data, token.data, tl[0].loc))
			_tl_clear(tl)
		else:
			_tl_append(tl, token)
	else:
		_error(UnexpectedTokenTypeError(token, "after a binary operator (expected a name)"))

def _parse_new_token_3(tl, code, token):
	""" TODO
	Assume that len(tl) == 3, that tl[0] and tl[2] are names and that tl[1] is either "|" or ":". """
	if tl[1].data == "|" and token.type == _TokenType.CODE:
		_print_dbg(_LvlDiff.NO, ("create-space \"{}\" | \"{}\" {{{}}}").format(
			tl[0].data, tl[2].data, " " if token.data.isempty() else " ... "), color = _NEGATIVE)
		code.append(InstructionCreatespace(tl[0].data, tl[2].data, token.data, tl[0].loc))
		_tl_clear(tl)
	elif tl[1].data == ":" and token.data == "|":
		_tl_append(tl, token)
	else:
		if tl[1].data == "|":
			_error(UnexpectedTokenTypeError(token, "(expected a code to complete a create-space instruction)"))
		else: # tl[1].data == ":"
			_error(UnexpectedTokenTypeError(token, "(expected a \"|\" to continue to create a create-port instruction)"))

def _parse_new_token_4(tl, code, token):
	""" TODO
	Assume that len(tl) == 4, that tl[0] and tl[2] are names, that tl[1] is ":" and that tl[3] is "|". """
	if token.type == _TokenType.NAME:
		_print_dbg(_LvlDiff.NO, "create-port \"{}\" : \"{}\" | \"{}\"".format(
			tl[0].data, tl[2].data, token.data), color = _NEGATIVE)
		code.append(InstructionCreateport(tl[0].data, tl[2].data, token.data, tl[0].loc))
		_tl_clear(tl)
	else:
		_error(UnexpectedTokenTypeError(token, "(expected a name to complete a create-port instruction)"))

_PARSE_NEW_TOKEN_FUNCTIONS = (
	_parse_new_token_0, _parse_new_token_1, _parse_new_token_2, _parse_new_token_3, _parse_new_token_4)
	# see _parse_new_token

def _parse_new_token(tl, code, token):
	""" Use the unparsed token sequence and the new givent token to update the sequence
	and to parse and add to the code a new instruction if possible.
	The instruction parser's internal state is strongly related to the length of the
	unparsed token sequence (this is totally accidental though), here they are:
	0: []
		[] + name -> [name] 1
		[] + nop  -> [] 0
		[] + op   -> ERROR
		[] + code -> ERROR
	1: [name]
		[name] + name -> (cut-link) [name] 1
		[name] + nop  -> (cut-link) [] 0
		[name] + op*  -> (port) [] 0
		[name] + op   -> [name, op] 2
		[name] + code -> ERROR
	2: [name, op]
		[name, op-] + name -> (create-link) [] 0
		[name, op/] + name -> (swap-link) [] 0
		[name, op:] + name -> [name, op:, name] 3
		[name, op|] + name -> [name, op|, name] 3
		[name, op]  + op   -> ERROR
		[name, op]  + nop  -> ERROR
		[name, op]  + code -> ERROR
	3: [name, op, name]
		[name, op|, name] + code -> (create-space) [] 0
		[name, op:, name] + op|  -> [name, op:, name, op|] 4
		[name, op, name]  + name -> ERROR
		[name, op, name]  + op   -> ERROR
		[name, op, name]  + nop  -> ERROR
		[name, op, name]  + code -> ERROR
	4: [name, op:, name, op|]
		[name, op:, name, op|] + name -> (create-port) [] 0
		[name, op:, name, op|] + op   -> ERROR
		[name, op:, name, op|] + nop  -> ERROR
		[name, op:, name, op|] + code -> ERROR
	Note that nop can be a nop instruction, an end-of-subcode or an end-of-file,
	those three acted exactly in the same way in every situation so they are all called nop now.
	"""
	_print_dbg(_LvlDiff.BEG, "tl parsing case {} with {}".format(len(tl), token.lowercase_type()))
	_PARSE_NEW_TOKEN_FUNCTIONS[len(tl)](tl, code, token)
	_print_dbg(_LvlDiff.END, "tl parsing end")

def _isnamechar(c):
	""" TODO """
	return ord("a") <= ord(c) <= ord("z") or ord("0") <= ord(c) <= ord("9")

def _readname(src, i):
	""" TODO """
	start = i
	while i < len(src) and _isnamechar(src[i]):
		i += 1
	return src[start:i], i

def _parse(src, root, i, line, filename):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "{}code parsing at {} line {} in file {}".format("" if root else "sub", i, line, filename))
	code = Code(Loc(i, line, filename))
	tl = [] # unparsed token sequence
	while True: # break is good practice
		if i >= len(src):
			_print_dbg(_LvlDiff.NO, "end of file {}".format(filename))
			_parse_new_token(tl, code, _Token(_TokenType.NOP, _TokenNopSubtype.EOF, Loc(i, line, filename)))
			break
		elif src[i].isspace():
			if src[i] == "\n":
				_print_dbg(_LvlDiff.NO, "end of line {}".format(line), color = _MAGENTA)
				line += 1
			i += 1
		elif src[i:].startswith("###"): # must stay before the "#" test for line comments
			_print_dbg(_LvlDiff.NO, "block comment")
			i += 3
			start = i
			while i < len(src) and (not src[i:].startswith("###")):
				if src[i] == "\n":
					line += 1
				i += 1
			if i >= len(src):
				_error(UnexpectedTokenTypeError(_Token(_TokenType.NOP, _TokenNopSubtype.EOF, Loc(i, line, filename)),
					"(expected a \"###\" to end the final block comment)"))
				# could be ignored.. oh well. u gotta end ur block comments
			_print_dbg(_LvlDiff.NO, "###{}###".format(src[start:i]))
			i += 3
		elif src[i] == "#":
			_print_dbg(_LvlDiff.NO, "line comment")
			i += 1
			start = i
			while i < len(src) and src[i] != "\n":
				i += 1
			_print_dbg(_LvlDiff.NO, "#{}".format(src[start:i]))
		elif src[i] == ".":
			_print_dbg(_LvlDiff.NO, "nop", color = _CYAN)
			_parse_new_token(tl, code, _Token(_TokenType.NOP, _TokenNopSubtype.INSTR, Loc(i, line, filename)))
			i += 1
		elif src[i] in ("*", "-", "/", ":", "|"):
			_print_dbg(_LvlDiff.NO, "op \"{}\"".format(src[i]), color = _CYAN)
			_parse_new_token(tl, code, _Token(_TokenType.OP, src[i], Loc(i, line, filename)))
			i += 1
		elif _isnamechar(src[i]):
			start = i
			name, i = _readname(src, i)
			_print_dbg(_LvlDiff.NO, "name \"{}\"".format(name), color = _CYAN)
			_parse_new_token(tl, code, _Token(_TokenType.NAME, name, Loc(start, line, filename)))
		elif src[i] == "{":
			_print_dbg(_LvlDiff.NO, "code", color = _GREEN)
			start = i
			i += 1
			subcode, i, line = _parse(src, False, i, line, filename)
			i += 1 # the trailing "}"
			_parse_new_token(tl, code, _Token(_TokenType.CODE, subcode, Loc(start, line, filename)))
		elif src[i] == "[":
			i += 1
			start = i
			while i < len(src) and src[i] != "]":
				i += 1
			if i >= len(src):
				_error(UnexpectedTokenTypeError(_Token(_TokenType.NOP, _TokenNopSubtype.EOF, Loc(i, line, filename)),
					"(expected a \"]\" to end the final code include)"))
			includefilename = src[start:i]
			i += 1 # the trailing "]"
			_print_dbg(_LvlDiff.NO, "code from file \"{}\"".format(includefilename), color = _GREEN)
			try:
				include_code = parse_file(includefilename)
			except OSError as os_error:
				_error(os_error)
			_parse_new_token(tl, code, _Token(_TokenType.CODE, include_code, Loc(start, line, filename)))
		elif src[i] == "}":
			if not root:
				_print_dbg(_LvlDiff.NO, "end of subcode")
				_parse_new_token(tl, code, _Token(_TokenType.NOP, _TokenNopSubtype.EOSC, Loc(i, line, filename)))
				break
			else:
				_error(UnexpectedTokenTypeError(_Token(_TokenType.NOP, _TokenNopSubtype.EOF, Loc(i, line, filename)),
					"(no mathcing \"{\" for this \"}\")"))
		else:
			_error(UnexpectedCharacterError(src[i], Loc(i, line, filename)))
	_print_dbg(_LvlDiff.END, "{}code parsing end".format("" if root else "sub"))
	return code, i, line

def parse(src, filename = ""):
	""" TODO """
	return _parse(src, True, 0, 1, filename)[0]

def parse_file(filepath):
	""" TODO
	An OSError is raised (by the open built-in function) if the file cannot be opened. """
	with open(filepath, "r") as file:
		src = file.read()
	return parse(src, filepath)

#### Execution section

class PortslangCodeException(PortslangException):
	""" TODO """

class CodeWithoutPortError(PortslangCodeException):
	""" TODO """

	def __init__(self, code):
		self.code = code
		super().__init__("non-empty code without a port is illegal")

class DuplicatePortName(PortslangCodeException):
	""" TODO """

	def __init__(self, code, name):
		self.code = code
		self.name = name
		super().__init__("a code containing multiple ports with the same \"{}\" is illegal".format(name))

class IllformedInstructionError(PortslangCodeException):
	""" TODO """

	def __init__(self, instruction):
		self.instruction = instruction
		super().__init__("instruction illformed at loc {}".format(instruction.loc))

class PortslangExecutionException(PortslangException):
	""" TODO """

class NotVisibleError(PortslangExecutionException):
	""" TODO """

	def __init__(self, name, instruction = None):
		self.name = name
		self.instruction = instruction
		super().__init__("\"{}\" doesn't name a visibe port where it should{}".format(
			self.name, "" if instruction == None else " so {} (at loc {}) can't be executed".format(
				str(self.instruction), str(self.instruction.loc))))

class NotSurfacePortError(PortslangExecutionException):
	""" TODO """

	def __init__(self, name, instruction = None):
		self.name = name
		self.instruction = instruction
		super().__init__("\"{}\" doesn't name a visibe port where it should{}".format(
			self.name, "" if instruction == None else " so {} (at loc {}) can't be executed".format(
				str(self.instruction), str(self.instruction.loc))))

class NotAvailableError(PortslangExecutionException):
	""" TODO """

	def __init__(self, name, instruction = None):
		self.name = name
		self.instruction = instruction
		super().__init__("\"{}\" isn't an available name where it should{}".format(
			self.name, "" if instruction == None else " so {} (at loc {}) can't be executed".format(
				str(self.instruction), str(self.instruction.loc))))

class Instruction:
	""" TODO """
	
	# TODO

class InstructionPort(Instruction):
	""" TODO """

	def __init__(self, name, loc):
		self.name = name
		self.loc = loc

	def __str__(self):
		return "port \"{}\" *".format(self.name)

	def _print_dbg(self, first_port = False):
		""" TODO """
		_print_dbg(_LvlDiff.NO, "{}{}".format("first " if first_port else "", str(self)), color = _YELLOW)

	def optimizedout(self):
		""" TODO """
		return False

	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self), color = _CYAN)
		port_end_track = spark.space.pt[self.name].end_track(debug = True)
		if port_end_track == None:
			_print_dbg(_LvlDiff.NO, "no end of track")
		elif port_end_track.isinstr():
			_print_dbg(_LvlDiff.NO, "instr end of track \"{}\"".format(port_end_track.name))
			spark.space = port_end_track.space
			spark.index = port_end_track.other
		elif port_end_track.isspecial():
			_print_dbg(_LvlDiff.NO, "special end of track \"{}\"".format(port_end_track.name), color = _NEGATIVE)
			execute_special(port_end_track.name, spark)
		_print_dbg(_LvlDiff.END, "port end")

class InstructionCutlink(Instruction):
	""" TODO """

	def __init__(self, name, loc):
		self.name = name
		self.loc = loc

	def __str__(self):
		return "cut-link \"{}\"".format(self.name)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, str(self), color = _CYAN)

	def optimizedout(self):
		""" TODO """
		return False

	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self))
		if self.name not in spark.space.pt:
			_error(NotVisibleError(self.name, instruction = self))
		spark.space.pt[self.name].cut_link()
		_print_dbg(_LvlDiff.END, "cut-link end")

class InstructionCreatelink(Instruction):
	""" TODO """

	def __init__(self, name_a, name_b, loc):
		self.name_a = name_a
		self.name_b = name_b
		self.loc = loc

	def __str__(self):
		return "create-link \"{}\" - \"{}\"".format(self.name_a, self.name_b)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, str(self), color = _CYAN)

	def optimizedout(self):
		""" TODO """
		return False

	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self))
		if self.name_a not in spark.space.pt:
			_error(NotVisibleError(self.name_a, instruction = self))
		if self.name_b not in spark.space.pt:
			_error(NotVisibleError(self.name_b, instruction = self))
		spark.space.pt[self.name_a].set_link(spark.space.pt[self.name_b])
		_print_dbg(_LvlDiff.END, "create-link end")

class InstructionSwaplink(Instruction):
	""" TODO """

	def __init__(self, name_a, name_b, loc):
		self.name_a = name_a
		self.name_b = name_b
		self.loc = loc

	def __str__(self):
		return "swap-link \"{}\" / \"{}\"".format(self.name_a, self.name_b)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, str(self), color = _CYAN)

	def optimizedout(self):
		""" TODO """
		return self.name_a == self.name_b
		
	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self))
		if self.name_a not in spark.space.pt:
			_error(NotVisibleError(self.name_a, instruction = self))
		if self.name_b not in spark.space.pt:
			_error(NotVisibleError(self.name_b, instruction = self))
		spark.space.pt[self.name_a].swap_link(spark.space.pt[self.name_b])
		_print_dbg(_LvlDiff.END, "swap-link end")

class InstructionCreateport(Instruction):
	""" TODO """

	def __init__(self, name_ref, name_same, name_other, loc):
		self.name_ref = name_ref
		self.name_same = name_same
		self.name_other = name_other
		self.loc = loc

	def __str__(self):
		return "create-port \"{}\" : \"{}\" | \"{}\"".format(self.name_ref, self.name_same, self.name_other)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, str(self), color = _GREEN)

	def optimizedout(self):
		""" TODO """
		return False

	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self), color = _GREEN)
		if self.name_ref not in spark.space.pt:
			_error(NotVisibleError(self.name_ref, instruction = self))
		port_ref = spark.space.pt[self.name_ref]
		if not port_ref.issurface():
			_error(NotSurfacePortError(self.name_ref, instruction = self))
		if self.name_same in spark.space.pt:
			_error(NotAvailableError(self.name_same, instruction = self))
		if port_ref.isspace():
			_print_dbg(_LvlDiff.NO, "create space port")
			space_same = spark.space
			space_other = port_ref.other.space
			if self.name_other in space_other.pt:
				_error(NotAvailableError(self.name_other, instruction = self))
			port_same = Port(self.name_same)
			port_other = Port(self.name_other)
			port_same.other = port_other
			port_other.other = port_same
			space_same.add_port(port_same)
			space_other.add_port(port_other)
		else: # port_ref.isspecial()
			_print_dbg(_LvlDiff.NO, "create special port")
			new_special_port = Port(self.name_same)
			spark.space.add_port(new_special_port)
			# This port should do nothing
			# Note that the spec says that this is undefined behavior and that the interpreter
			# should raise an error (or that it shouldn't, depending on if I changed the spec
			# after I typed this comment)..
		_print_dbg(_LvlDiff.END, "create-port end", color = _GREEN)

class InstructionCreatespace(Instruction):
	""" TODO """

	def __init__(self, name_ext, name_int, code, loc):
		self.name_ext = name_ext
		self.name_int = name_int
		self.code = code
		self.loc = loc

	def __str__(self):
		return "create-space \"{}\" | \"{}\"".format(self.name_ext, self.name_int)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, str(self), color = _GREEN)
		if self.code.isempty():
			_print_dbg(_LvlDiff.NO, "empty-code { }")
		else:
			self.code._print_dbg()

	def optimizedout(self):
		""" TODO """
		return False

	def execute(self, spark):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, str(self), color = _GREEN)
		if self.name_ext in spark.space.pt:
			_error(NotAvailableError(self.name_ext, instruction = self))
		new_space = Space(self.code if not self.code.isempty() else spark.space.code)
		port_ext = Port(self.name_ext)
		port_int = Port(self.name_int)
		port_ext.other = port_int
		port_int.other = port_ext
		spark.space.add_port(port_ext)
		new_space.add_port(port_int)
		port_int.set_link(new_space.pt[new_space.code.first_port_name])
		_print_dbg(_LvlDiff.END, "create-space end", color = _GREEN)

class Code:
	""" TODO
	The Code class has the __getitem__ magic method implemented so that one can do
		code = Code()
		...
		instr_8 = code[8]
		port_instr_named_joe = code["joe"]
	Once created by the parser, a Code object should be considered read-only.
	The parser should only add instruction to it through the append method.
	See the run function to see how to run the produced Code object. """

	def __init__(self, loc):
		self.instrs = [] # instructions
		self.pit = {} # port name-to-index table
		self.first_port_name = None
		self.empty = True
		self.loc = loc

	def __getitem__(self, key):
		if type(key) == int:
			if 0 <= key < len(self.instrs):
				return self.instrs[key]
			else:
				raise IndexError # TODO do better than this
		elif type(key) == str:
			if key in self.pit:
				return self.instrs[self.pit[key]]
			else:
				raise KeyError # TODO do better than this

	def __len__(self):
		return len(self.instrs)

	def _print_dbg(self):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "code at loc {}".format(str(self.loc)))
		for instr in self.instrs:
			if type(instr) == InstructionPort and instr.name == self.first_port_name:
				instr._print_dbg(first_port = True)
			else:
				instr._print_dbg()
		_print_dbg(_LvlDiff.END, "code end")

	def isempty(self):
		""" TODO """
		return self.empty
		# this method is extremely useful and a call to it cannot be replaced by an access to
		# an attribute because of the object oriented programming paradigm principles and rules
		# that say that it shall not be done

	def append(self, instr):
		""" TODO """
		self.empty = False
		if instr.optimizedout():
			_print_dbg(_LvlDiff.NO, "optimized out")
		self.instrs.append(instr)
		index = len(self.instrs) - 1
		_print_dbg(_LvlDiff.NO, "added to index {}".format(index))
		if type(instr) == InstructionPort:
			self.pit[instr.name] = index
			if self.first_port_name == None:
				self.first_port_name = instr.name

	def check(self, initial_port_names):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "code check at loc {}".format(self.loc))
		if self.first_port_name == None:
			_error(CodeWithoutPortError(self))
		names = set(initial_port_names)
		for instr in self.instrs:
			if type(instr) == InstructionCreatespace and (not instr.code.isempty()):
				instr.code.check([instr.name_int])
			elif type(instr) == InstructionPort:
				if instr.name in names:
					_error(DuplicatePortName(self, instr.name))
				else:
					names.add(instr.name)
		_print_dbg(_LvlDiff.END, "code check end")

	def run(self):
		""" TODO """
		run(self) # for no reason, this is not a method

class Port:
	""" TODO """

	def __init__(self, name):
		self.name = name
		self.space = None # set by Space.add_port
		self.link = None
		self.other = None

	def isinstr(self):
		""" TODO """
		return type(self.other) == int

	def isspace(self):
		""" TODO """
		return type(self.other) == Port

	def isspecial(self):
		""" TODO """
		return self.other == None

	def issurface(self):
		""" TODO """
		return self.isspace() or self.isspecial()

	def cut_link(self):
		""" TODO """
		if self.link != None:
			self.link.link = None
			self.link = None

	def set_link(self, other_port):
		""" TODO """
		self.cut_link()
		other_port.cut_link()
		self.link = other_port
		other_port.link = self

	def swap_link(self, other_port):
		""" TODO """
		if self.link is not other_port:
			self.link, other_port.link = other_port.link, self.link
		# If self.link is other_port, then swapping self's link with other_port's link consists in
		# inverting the link's orientation (and links don't have an orientation in Ports, so it consists
		# in doing nothing (doing the same thing as if self.link is not other_port can result in
		# each port being linked to themselves, which is not expected to happen)).
		# Note that such an instruction should be optimized out.

	def end_track(self, debug = False):
		""" TODO """
		if self.link == None:
			if debug:
				_print_dbg(_LvlDiff.NO, "{} -> (no-link)".format(self.name))
			return None
		elif self.link.isspace():
			if debug:
				_print_dbg(_LvlDiff.NO, "{} -> {} (space)".format(self.name, self.link.name))
			return self.link.other.end_track(debug = debug)
		else:
			if debug:
				_print_dbg(_LvlDiff.NO, "{} -> {} (no-space)".format(self.name, self.link.name))
			return self.link

class Space:
	""" TODO """

	def __init__(self, code):
		self.code = code
		self.pt = {} # port name-to-port table
		for name, index in self.code.pit.items():
			port = Port(name)
			port.other = index
			self.add_port(port)

	def add_port(self, port):
		""" TODO """
		self.pt[port.name] = port
		port.space = self

class Spark:
	""" TODO """

	def __init__(self, port_origin):
		port_start = port_origin.end_track() # port_start.isinstr() assumed
		self.space = port_start.space
		self.root_space = self.space # used in the comeoutof method
		self.index = port_start.other
		self.next_special = None # see comeoutof
		self.running = False

	def incr(self):
		""" TODO """
		self.index = (self.index + 1) % len(self.space.code)

	def run(self):
		""" TODO """
		self.running = True
		while self.running:
			self.space.code[self.index].execute(self)
			while self.next_special != None:
				name = self.next_special
				self.next_special = None
				execute_special(name, self) # So that two special ports linked and looping doesn't stack overflow
			self.incr()

	def comeoutof(self, name):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "spark come out of \"{}\"".format(name))
		port_restart = self.root_space.pt[name].end_track(debug = True)
		if port_restart == None:
			_print_dbg(_LvlDiff.NO, "so no")
		elif port_restart.isinstr():
			_print_dbg(_LvlDiff.NO, "instruction ok")
			self.space = port_restart.space
			self.index = port_restart.other
		else: # port_restart.isspecial()
			_print_dbg(_LvlDiff.NO, "special ok")
			self.next_special = port_restart.name # see the run method
		_print_dbg(_LvlDiff.END, "spark come out of end")

def run(code):
	""" TODO
	Note that code.run() is equivalent to run(code) if code is a Code object. """
	root_space = Space(code)
	for name in SPECIAL_PORT_TABLE.keys():
		special_port = Port(name)
		special_port.other = None
		root_space.add_port(special_port)
	root_space.pt["o"].set_link(root_space.pt[root_space.code.first_port_name])
	spark = Spark(root_space.pt["o"])
	spark.incr() # so that execution doesn't end right away
	spark.run()

def run_source(src):
	""" TODO """
	_print_dbg(_LvlDiff.NO, "parsing the source code", color = _YELLOW)
	code = parse(src)
	_print_dbg(_LvlDiff.NO, "displaying the code", color = _YELLOW)
	_print_dbg(_LvlDiff.NO, code)
	_print_dbg(_LvlDiff.NO, "checking the code", color = _YELLOW)
	code.check(SPECIAL_PORT_TABLE.keys())
	_print_dbg(_LvlDiff.NO, "running the code", color = _YELLOW)
	run(code)

def run_file(source_file_path):
	""" TODO """
	_print_dbg(_LvlDiff.NO, "parsing the source code", color = _YELLOW)
	code = parse_file(source_file_path) # here is the difference with run_source
	_print_dbg(_LvlDiff.NO, "displaying the code", color = _YELLOW)
	_print_dbg(_LvlDiff.NO, code)
	_print_dbg(_LvlDiff.NO, "checking the code", color = _YELLOW)
	code.check(SPECIAL_PORT_TABLE.keys())
	_print_dbg(_LvlDiff.NO, "running the code", color = _YELLOW)
	run(code)

#### Special section

class PortslangSpecialException(PortslangExecutionException):
	""" TODO """

def _bits_to_string(bits):
	""" TODO """
	return "".join([str(bit) for bit in bits])

class BitBuffer:
	""" TODO """

	def __init__(self):
		self.bits = []

	def __getitem__(self, key):
		return self.bits[key]

	def __len__(self):
		return len(self.bits)

	def append(self, bit):
		""" TODO """
		_print_dbg(_LvlDiff.NO, "bit buffer appended {}".format(bit))
		self.bits.append(bit)

	def isempty(self):
		""" TODO """
		return len(self.bits) == 0

	def clear(self):
		""" TODO """
		_print_dbg(_LvlDiff.NO, "bit buffer [{}] cleared".format(_bits_to_string(self.bits)))
		self.bits.clear()

	def popfront(self):
		""" TODO """
		# assume that (not self.isempty()) is True
		_print_dbg(_LvlDiff.NO, "bit buffer popped {}".format(self.bits[0]))
		return self.bits.pop(0)

	def popstring(self):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "bit buffer to string [{}]".format(_bits_to_string(self.bits)))
		array = bytearray()
		while len(self.bits) >= 8:
			bytebits = self.bits[:8]
			self.bits = self.bits[8:]
			byte = 0
			for i in range(8):
				byte += bytebits[i] << (7-i)
			array.append(byte)
			_print_dbg(_LvlDiff.NO, "byte [{}] evaluates to {}".format(_bits_to_string(bytebits), byte))
		if len(self.bits) > 0:
			_print_dbg(_LvlDiff.NO, "remaining bits [{}] discarded".format(_bits_to_string(self.bits)))
			self.bits.clear()
		string = array.decode(encoding = "utf-8")
		_print_dbg(_LvlDiff.END, "bit buffer to string end {}".format(repr(string)))
		return string

	def appendstring(self, string):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "string to bit buffer {}".format(repr(string)))
		start = len(self.bits)
		for char in string:
			array = char.encode(encoding = "utf-8")
			bits = []
			for b in array:
				for i in range(8):
					bits.append(int(bool(b & (1 << (7-i))))) # int(bool(...)) uwu
			self.bits += bits
			_print_dbg(_LvlDiff.NO, "char \"{}\" is encoded to [{}]".format(char, _bits_to_string(bits)))
		_print_dbg(_LvlDiff.END, "string to bit buffer end [{}]".format(_bits_to_string(self.bits[start:])))

	def appendint32(self, int32):
		""" TODO """
		_print_dbg(_LvlDiff.BEG, "int32 to bit buffer {}".format(int32))
		start = len(self.bits)
		int32 = (int32 + (2**32)) % (2**32)
		for i in range(32):
			self.bits.append(int(bool(int32 & (1 << (31-i)))))
		_print_dbg(_LvlDiff.END, "int32 to bit buffer end [{}]".format(_bits_to_string(self.bits[start:])))

def _change_mode(mode):
	""" TODO """
	if SPECIAL_SHARED_DATA["mode"] != mode:
		_print_dbg(_LvlDiff.NO, "mode turned to {}".format(mode))
		SPECIAL_SHARED_DATA["mode"] = mode
		SPECIAL_SHARED_DATA["bits"].clear()

def special_nop(spark):
	""" TODO
	Not in SPECIAL_PORT_TABLE, but is used as the default value when using SPECIAL_PORT_TABLE.get. """
	_print_dbg(_LvlDiff.NO, "special nop", color = _BLUE)

def special_origin(spark):
	""" TODO """
	_print_dbg(_LvlDiff.NO, "special origin", color = _BLUE)
	spark.running = False # gonne until next Ports program run

def special_output_zero(spark):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "special output zero", color = _BLUE)
	_change_mode("out")
	SPECIAL_SHARED_DATA["bits"].append(0)
	_print_dbg(_LvlDiff.END, "special output zero end", color = _BLUE)

def special_output_one(spark):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "special output one", color = _BLUE)
	_change_mode("out")
	SPECIAL_SHARED_DATA["bits"].append(1)
	_print_dbg(_LvlDiff.END, "special output one end", color = _BLUE)

def special_output_flush(spark):
	""" TODO """
	if _debug_enabled:
		_print_dbg(_LvlDiff.BEG, "special output flush", color = _BLUE)
		_change_mode("out")
		_print_dbg(_LvlDiff.NO, repr(SPECIAL_SHARED_DATA["bits"].popstring()))
		_print_dbg(_LvlDiff.END, "special output flush end", color = _BLUE)
	else:
		_change_mode("out")
		print(SPECIAL_SHARED_DATA["bits"].popstring(), end = "", flush = True)

def special_output_system(spark):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "special output system", color = _BLUE)
	if not SPECIAL_SHARED_DATA["osok"]:
		_error(PortslangSpecialException("the use of the \"os\" special port is not allowed without the -s flag"))
		# See the command line option parsing
	_change_mode("out")
	command = SPECIAL_SHARED_DATA["bits"].popstring()
	_print_dbg(_LvlDiff.NO, repr(command), color = _GREEN)
	result = _subprocess.run(command, shell = True, capture_output = True, encoding = "utf-8")
	_print_dbg(_LvlDiff.NO, "exit statuts {}".format(result.returncode), color = _GREEN)
	SPECIAL_SHARED_DATA["bits"].appendint32(result.returncode)
	_print_dbg(_LvlDiff.NO, "stdout {}".format(repr(result.stdout)))
	SPECIAL_SHARED_DATA["bits"].appendstring(result.stdout)
	if result.stderr:
		_print_dbg(_LvlDiff.NO, "stderr {}".format(repr(result.stderr)))
		for _ in range(8):
			SPECIAL_SHARED_DATA["bits"].append(0)
		SPECIAL_SHARED_DATA["bits"].appendstring(result.stderr)
	_print_dbg(_LvlDiff.END, "special output system end", color = _BLUE)

def special_ask_input(spark):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "special ask input", color = _BLUE)
	_change_mode("in")
	SPECIAL_SHARED_DATA["bits"].appendstring(input())
	_print_dbg(_LvlDiff.END, "special ask input end", color = _BLUE)

def special_input_read(spark):
	""" TODO """
	_print_dbg(_LvlDiff.BEG, "special read input", color = _BLUE)
	_change_mode("in")
	if len(SPECIAL_SHARED_DATA["bits"]) >= 1:
		bit = SPECIAL_SHARED_DATA["bits"].popfront()
		if bit == 0:
			spark.comeoutof("o0")
		else: # bit == 1
			spark.comeoutof("o1")
	_print_dbg(_LvlDiff.END, "special read input end", color = _BLUE)

SPECIAL_PORT_TABLE = {
	"o":  special_origin,
	"o0": special_output_zero,
	"o1": special_output_one,
	"of": special_output_flush,
	"os": special_output_system,
	"ia": special_ask_input,
	"ir": special_input_read,
}

SPECIAL_SHARED_DATA = {
	"bits": BitBuffer(),
	"mode": "none", # mode of the buffer named "bits"
	"osok": False, # see special_output_system and the -s flag
}

def execute_special(name, spark):
	""" TODO """
	(SPECIAL_PORT_TABLE.get(name, special_nop))(spark)

#### Main section

# If one thinks that there are too much calls to _print_dbg, one might be right.

if __name__ == "__main__":
	from sys import argv
	from os import path
	ownpath = argv[0]
	args = argv[1:]
	if "--no-ansi-codes" in args:
		_ansi_codes_enabled = False # Needed before any printing operation
	if ("--debug" in args) or ("-d" in args):
		_debug_enabled = True # Needed before anything else
	_print_dbg(_LvlDiff.NO, "parsing the command line arguments", color = _YELLOW)
	_print_dbg(_LvlDiff.BEG, "command line arguments parsing")
	source_file_path = None
	help_message_asked = False
	version_asked = False
	for arg in args:
		if (arg.startswith("-") and len(arg) == 2) or arg.startswith("--"):
			_print_dbg(_LvlDiff.BEG, "option \"{}\" parsing".format(arg))
			if arg in ("-e", "--no-ansi-codes"):
				_print_dbg(_LvlDiff.NO, "no ANSI codes used by the interpreter")
				_print_dbg(_LvlDiff.NO, "this is already in effect", color = _MAGENTA)
				# Note that it seems stupid to output this debug message with color, and it is stupid
				# but this year it's my birthday and I really wanted to do this
			elif arg in ("-d", "--debug"):
				_print_dbg(_LvlDiff.NO, "debug mode is activated")
				_print_dbg(_LvlDiff.NO, "this is already in effect", color = _MAGENTA)
			elif arg in ("-h", "--help"):
				_print_dbg(_LvlDiff.NO, "print the help message after the command line arguments parsing")
				help_message_asked = True
			elif arg in ("-v", "--version"):
				_print_dbg(_LvlDiff.NO, "print the interpreter version after the command line arguments parsing")
				version_asked = True
			elif arg in ("-s", "--os-ok"):
				_print_dbg(_LvlDiff.NO, "\"os\" special port enabled")
				SPECIAL_SHARED_DATA["osok"] = True
			else:
				_print_dbg(_LvlDiff.NO, "unknown option", color = _RED)
				_print_dbg(_LvlDiff.NO, "option ignored")
			_print_dbg(_LvlDiff.END, "option parsing end")
		else:
			_print_dbg(_LvlDiff.BEG, "argument \"{}\" parsing".format(arg))
			_print_dbg(_LvlDiff.NO, "source file path", color = -1)
			if path.isfile(arg):
				_print_dbg(_LvlDiff.NO, "refers to an existing file")
				if source_file_path == None:
					if arg.endswith(".ports"):
						_print_dbg(_LvlDiff.NO, "\"ports\" extention detected")
					else:
						_print_dbg(_LvlDiff.NO, "missing \"ports\" extention ignored")
						# Was this even useful ?
					_print_dbg(_LvlDiff.NO, "registered as the source file path", color = _CYAN)
					source_file_path = arg
				else:
					_print_dbg(_LvlDiff.NO, "argument ignored because a source file path have already been registered")
					_print_dbg(_LvlDiff.NO, "the already registered source file path is \"{}\"".format(source_file_path))
			else:
				_print_dbg(_LvlDiff.NO, "argument ignored because it doesn't refer to an exisiting file")
			_print_dbg(_LvlDiff.END, "argument parsing end")
	_print_dbg(_LvlDiff.END, "command line arguments parsing end")
	if help_message_asked:
		_print_dbg(_LvlDiff.NO, "the help message will now be printed", color = _YELLOW)
		print("usage:")
		print("    python3 {} <src-file-path> [options]".format(ownpath))
		print("options:")
		print("-d  --debug          Turn on debug output.")
		print("-e  --no-ansi-codes  Disable the use of ansi escape codes in debeug output.")
		print("-h  --help           Display this help message.")
		print("-v  --version        Display the interpreter's version.")
		print("-s  --os-ok          Enable the use of the \"os\" special port.")
	if version_asked:
		_print_dbg(_LvlDiff.NO, "the interpreter version will now be printed", color = _YELLOW)
		print("\"Ports\" esoteric programming language interpreter")
		print("Version {} of the Python 3 reference interpreter".format(__version__))
	if source_file_path == None:
		if _debug_enabled:
			_print_dbg(_LvlDiff.NO, "no existing source file", color = _MAGENTA)
			_print_dbg(_LvlDiff.NO, "tip: use the -h option for help", color = _MAGENTA)
		else:
			print("no existing source file")
			print("tip: use the -h option for help")
	else:
		_print_dbg(_LvlDiff.NO, "now what u ve been waiting for", color = _MAGENTA)
		run_file(source_file_path)

# TODO: add GUI/turttle/mouse+keyboard special ports (with colors and events in the bitbuffer and stuff)
# TODO: a flag that says "stop at each yellow line (important steps) and print out what ya got"
# TODO: add a flag that allow to give the source code in the command line instead of giving the source file path
# TODO: add a flag that says that the source code is sys.stdin.read()
# TODO: add a flag that forbids the use of the "x|o[filepath]" syntax to include files
# TODO: add an option that takes a name N and that says "breakpoint on each port instruction named N" with some dbg shits
# TODO: add parameters and return types to all functions (or not)
# TODO: implement this in optimized C
# TODO: fill the doc strings (this will reduce by a lot the number of TODOs)
# TODO: delete the optimizeout methods that mainly return False with a probability of 142%
