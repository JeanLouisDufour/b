# pour les nouveaux .po : ajout de SET et >>
#
#
import os
import ply.lex as lex
from toposort import toposort_flatten

literals = r"*+-/:<=>|" + r"?!#%&'(),;[]^{}~$" # si . ici, alors .. ne lexe pas
# '\\' ne passe pas dans le parser
t_Dot = r'\.'
t_DblDot = r'\.\.'
# t_BackSlash = '\\'
par_counter = 0
def t_lpar(t):
	r'\('
	global par_counter
	par_counter += 1
	t.type = '('
	return t
def t_rpar(t):
	r'\)'
	global par_counter
	assert par_counter > 0
	par_counter -= 1
	t.type = ')'
	return t

def t_comment(t):
	r'/\*(.|\n)*?\*/'
	r'/\*([^\*]|\n|\*[^/])*?\*/'
	# print('comment')
	# print(t)
	t.lexer.lineno += t.value.count('\n')

def t_SYMBOL_1(t):
	r'=[=>]?'
	s = t.value
#	print(('SYMBOL',s))
	if len(s) == 1:
		t.type = s
	elif s[1] == '=':
		t.type = 'DblEqu'
	else:
		t.type = 'EquSup'
	return t
		
def t_SYMBOL(t):
	r'[\*\+\-/:<>\\\|][\*\+\-/:<=>\\\|]*'
	s = t.value
#	print(('SYMBOL',s))
	if len(s) == 1:
		if s == '\\':
			t.type = 'Op60l'
		else:
			t.type = s
	else:
		v = symbol_d.get(s)
		if v:
			t.type = v
		else:
			print('BAD SYMBOL : '+s)
			print(t)
			assert False
	return t

G,D = False,True

symbol_d = {
	'<>': 'InfSup',
	'<--': 'InfDblMinus',
	'||': 'DblBar',
	"=>": 'EquSup',
	"::": 'DblColon',
	"<=>": 'InfEquSup',
#	":": 'Colon',
	"==": 'DblEqu',
#	"=": 'Equ',
	":=": 'ColonEqu',
#	'-': 'Minus', # 210 en unaire
#	"+": 'Plus',
#	"/": 'Slash',
}
op_d = {
#	'Op10l': ("|",),
	'Op11l': ("[]",), ### si on remplace par '[' ']', on a un S/R
	'Op20l': ("==>",),
	'Op30l': (),
	'Op40l': (),
	'Op60l': ('\\',),
	'Op110l': ("/<<:","/<:","<<:","<:")+('>>',), ## nvx .po
	'Op120l': (">->>",">+>>",">+>",">->","<->"),
	'Op125l': ("+->>","+->","-->","-->>",),
	'Op160l': ("/:","/=",">=",">","<=","<","/|\\","\\|/","<-","->","^","><","<+","|>","<|","|>>","<<|","|->","/\\","\\/"),
	'Op170l': (),
	'Op180l': (),
	'Op190l': (),
	'Op200r': ('**',),
	'Op210': (),
	'Op220r': (),
	'Op250l': (),
}
for k,v in op_d.items():
	for tok in v:
		assert tok not in symbol_d, tok
		symbol_d[tok] = k

kw_machine = {  ## sauf INVARIANT et DEFINITIONS
"ABSTRACT_CONSTANTS" ,
"ABSTRACT_VARIABLES" ,
"ASSERTIONS" ,
"CONCRETE_CONSTANTS" ,
"CONCRETE_VARIABLES" ,
"CONSTANTS" ,
"CONSTRAINTS" ,
"EXTENDS" ,
"IMPORTS" ,
"INCLUDES" ,
"INITIALISATION" ,
"LOCAL_OPERATIONS",
"OPERATIONS" ,
"PROMOTES" ,
"PROPERTIES" ,
"REFINES" ,
"SEES" ,
"USES" ,
"VALUES" ,
"VARIABLES" ,
"VISIBLE_VARIABLES" ,
}
kw_par_counter = 0
kw_left_paren = { ### donnent lieu a un END
"ANY" ,
"ASSERT" ,
"BEGIN" ,
"CASE" ,
"CHOICE" ,
"EITHER" ,
"LET" ,
"PRE" ,
"IF" ,
"SELECT" ,
"VAR" ,
"WHILE" ,
}
kw_start_file = { ## sauf DEFINITIONS
"IMPLEMENTATION" ,
"MACHINE" ,
"REFINEMENT" ,
"THEORY" , ### ??????
}
reserved_set = kw_start_file | {"DEFINITIONS"} | kw_machine | {"INVARIANT"} | kw_left_paren | {
"BE" ,
"DO" ,
"ELSE" ,
"ELSIF" ,
"END" ,
"IN" ,
"INTER",
"IS" ,
"mod" ,
"not" ,
"OF" ,
"OR" ,
"or" ,
"PI",
"SET" , ## nvx .po
"SETS" ,
"SIGMA",
"skip" ,
"THEN" ,
"UNION",
"VARIANT" ,
"WHEN" ,
"WHERE" ,
}

reserved_d = {t:'_{}_'.format(t) for t in reserved_set}

def t_Identifier_DOT(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_0-9]+)+'
	return t

def t_Identifier(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*'
	global kw_par_counter, par_counter
	tv = t.value
	s = reserved_d.get(tv)
	if s:
		t.type = s
		if tv in kw_left_paren:
			kw_par_counter += 1
		elif tv == 'END':
			assert kw_par_counter >= 0 # le dernier END est a -1
			kw_par_counter -= 1
		elif tv in kw_start_file or tv == 'DEFINITIONS':
			kw_par_counter = par_counter = 0
	return t

def t_DecimalFloat(t):
	r'\d+\.\d+([eE][+-]?\d+)?'
	t.value = float(t.value)
	return t

def t_DecimalInt(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_StringLit(t):
	r'\"(\\\"|[^\n\"])*\"'
	return t

t_ignore_space = '[ \t\x0c]+'  ## \r pour Py27, \xef pour i trema

def t_newline(t):
	r'\n'
	t.lexer.lineno += 1 # len(t.value)

def t_newline_2(t):
	r'\r\n'
	t.lexer.lineno += 1 # len(t.value)

def t_error(t):
	c = t.value[0]
	oc = ord(c)
	if oc >= 128: ### par ex. \xef pour i trema
		print("SKIPPING char '{}' ({}) at line {}".format(c,oc,t.lexer.lineno))
		t.lexer.skip(1)
	else:
		print("BAD char '{}' ({})".format(c,oc))
		print(t)
		assert False
	
tokens = (
	'DecimalFloat',
	'DecimalInt',
	'Dot','DblDot',
	'Identifier', 'Identifier_DOT',
	'StringLit',
	'Op30l', 'Op40l', 'Op170l', 'Op180l', 'Op190l', 'Op210', 'Op220r', 'Op250l' ## 'Op60l', 
	) + tuple(reserved_d.values()) + tuple(set(symbol_d.values()))

lexer = lex.lex() # 

########## bpp ########################

class Lexer_pp:
	
	def_file_raw_d = {} ## "foo.def" -> {d1 d2 ...}
	def_file_exp_d = {}
	
	@staticmethod
	def _expand_definitions(d):
		""
		def_files = [k for k,v in d.items() if v == (None, None)]
		for df in def_files:
			if df in Lexer_pp.def_file_exp_d:
				del d[df]
				df_d = Lexer_pp.def_file_exp_d[df]
				for k,v in df_d.items():
					assert k not in d
					d[k] = v
			else:
				print("WARNING : {} not found".format(df))
		
	##################################
	
	def _init_definitions(self):
		""
		self.in_definitions = False # en dehors de DEFINITIONS
		self.definition_d = {}
		self.substituted_tok_list = []
		
	def _register_definition(self, name, pars, tokens):
		""
		assert name not in self.definition_d
		if pars == tokens == None:
			assert name[0] == name[-1] == '"', name
			name = name[1:-1]
			assert name.endswith('.def'), name
		else:
			assert name.isidentifier()
		self.definition_d[name] = (pars, tokens)
	
	def _finalize_definitions(self):
		""
		Lexer_pp._expand_definitions(self.definition_d)
		
	##############
		
	def __init__(self, lexobj, filename=None):
		""
		self.lexobj = lexobj
		self._init_definitions()
	
	def input(self, s):
		""
		self.lexobj.input(s)
		self._init_definitions()
	
	def token(self):
		"""
		on delivre au parser les def, mais on omet == et ce qui suit
		"""
		# print('bpp')
		#tok = self.lexobj.token()
		if self.substituted_tok_list:
			tok = self.substituted_tok_list[0]
			self.substituted_tok_list = self.substituted_tok_list[1:]
		elif self.in_definitions: ### on skippe tout jusqu'a la fin des def
			assert par_counter==kw_par_counter==0
			assert self.substituted_tok_list == []
			tok = self.lexobj.token()
			assert tok != None
			end_of_def = False
			while not end_of_def: # tok 
				"""
				- tok en entree est juste apres DEFINITIONS ou ;
					en particulier (sauf erreur de syntaxe), il n'est pas None
				- tok en sortie vaut le premier token apres les definitions
					en particulier, il peut etre None (sur un .def)
				"""
				def_name = tok.value
				if tok.type == 'StringLit':
					def_pars = def_tokens = None
					self.substituted_tok_list.append(tok)
					tok = self.lexobj.token()
				elif tok.type == 'Identifier':
					self.substituted_tok_list.append(tok)
					tok = self.lexobj.token()
					if tok.type == '(':
						def_pars = []
						tok = self.lexobj.token()
						while tok.type == 'Identifier':
							def_pars.append(tok.value)
							tok = self.lexobj.token()
							assert tok.type in (',',')')
							tok = self.lexobj.token()
					else:
						def_pars = None
					assert tok.value in ('==','='), tok.value
					def_tokens = []
					tok = self.lexobj.token()
					while tok and not (tok.type==';' and par_counter==kw_par_counter==0) and not(tok.value in kw_machine):
						def_tokens.append(tok)
						tok = self.lexobj.token()
				else:
					assert False, tok
				if tok and tok.type == ';':
					self.substituted_tok_list.append(tok)
					tok = self.lexobj.token()
				else: ### fin de DEFINITIONS
					end_of_def = True
				self._register_definition(def_name, def_pars, def_tokens)
			assert tok == None or tok.value in kw_machine or tok.value=="INVARIANT", tok.value
			self.in_definitions = False
			if tok: # on est dans une machine
				self._finalize_definitions()
			else:   # on est dans un .def
				pass
			self.substituted_tok_list.append(tok)
			tok = self.substituted_tok_list.pop(0)
		# now, not in_definitions nor in_substitution
		else:
			tok = self.lexobj.token()
			if tok and tok.value == 'DEFINITIONS':
				self.in_definitions = True
			elif tok and tok.type == 'Identifier' and tok.value in self.definition_d:
				def_name = tok.value
				def_pars,def_tokens = self.definition_d[def_name]
				if def_pars:
					par_l = []
					memo_par_counter = par_counter
					tok = self.lexobj.token()
					tok_l = [tok]
					assert tok.value == '('
					tok = self.lexobj.token()
					while not(tok.value==')' and par_counter==memo_par_counter):
						tok = self.lexobj.token()
						if tok.value == ',' and par_counter==memo_par_counter+1:
							par_l.append(tok_l)
							tok_l = []
						else:
							tok_l.append(tok)
					par_l.append(tok_l[:-1])
					assert len(def_pars) == len(par_l)
					par_d = {k: (None,v) for k,v in zip(def_pars, par_l)}
				else:
					par_d = {}
				self.substituted_tok_list = def_tokens ### TBC avec subst
				tok = self.substituted_tok_list[0]
				self.substituted_tok_list = self.substituted_tok_list[1:]
		return tok
	
	# Iterator interface
	def __iter__(self):
		return self
	def next(self):
		t = self.token()
		if t is None:
			raise StopIteration
		return t
	__next__ = next

lexer = Lexer_pp(lexer)

def init_def_files(chemin):
	""
	depends_on = {}
	Lexer_pp.def_file_raw_d = {}
	Lexer_pp.def_file_exp_d = {}
	assert os.path.exists(chemin)
	for root, dirs, files in os.walk(chemin):
		for fn in files:
			if fn.endswith('.def'):
				fp = os.path.join(root,fn)
				print('*******************************************')
				print(fp)
				fd = open(fp)
				prg = fd.read()
				fd.close()
				lexer.input(prg)
				for t in lexer:
					pass
				assert fn not in Lexer_pp.def_file_raw_d
				Lexer_pp.def_file_raw_d[fn] = lexer.definition_d
				depends_on[fn] = {k for k,v in lexer.definition_d.items() if v == (None, None)}
	def_file_l = toposort_flatten(depends_on)
	for df in def_file_l:
		Lexer_pp.def_file_exp_d[df] = d = Lexer_pp.def_file_raw_d[df].copy()
		Lexer_pp._expand_definitions(d)

if __name__ == '__main__':
	s = """
	a b -12 . 3.14 .. MACHINE == => = * * ** /**/ * /* foo
	bar *
	*****/ ok
	"""
	s1 = """DEFINITIONS "foo.def" ; a== b
	VARIABLES bar,a
	"""
	print(s)
	lexer.input(s)
	for t in lexer: print(t)
	#
	p = r'E:\papa\mbd\b\livraison_officielle_04080951\b\src'
	init_def_files(p)
