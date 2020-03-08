import ply.yacc as yacc
# import ply2yacc
# Get the token map from the lexer.  This is required.
from b_lexer import tokens, lexer
from b_util import expr_split
################
import sys, functools, itertools

def make_seq_lr(p):
	""
	lp = len(p)
	if lp >= 3:
		p[1].append(p[lp-1])
		p[0] = p[1]
	elif lp >= 2:
		p[0] = [p[1]]
	else:
		p[0] = []
		
def make_seq_rr(p):
	""
	lp = len(p)
	if lp >= 3:
		p[0] = [p[1]]+p[lp-1]
	elif lp >= 2:
		p[0] = [p[1]]
	else:
		p[0] = []

def get_operations(ol):
	""
	d = {}
	for o in ol:
		[eq,hd,tl] = o
		assert eq == '='
		par_in = []
		par_out = []
		if isinstance(hd,str):
			name = hd
		elif isinstance(hd,list) and hd[0] == '(':
			[_, name, inputs] = hd
			par_in = expr_split(inputs)
		elif isinstance(hd,list) and hd[0] == '<--':
			[_, outputs, head] = hd
			par_out = expr_split(outputs)
			if isinstance(head,str):
				name = head
			else:
				assert isinstance(head,list) and head[0]=='('
				[_, name, inputs] = head
				par_in = expr_split(inputs)
		else:
			assert False, hd
		assert name not in d and name.isidentifier(), name
		d[name] = (par_in, par_out, tl)
	return d
	
start = 'implementation'
# %start definition_file

def p_implementation(p): # EOF
	"""implementation : composant
	| clause_definitions
	"""
	p[0] = p[1]

def p_composant(p):
	"""composant : machine_abstraite
 | raffinement
 | implantation
 | expression
	"""
	p[0] = p[1]

def p_machine_abstraite(p):
	"""machine_abstraite : _MACHINE_ Ident Ident_PLUSComma_PAR_OPT clause_machine_abstraite_STAR _END_
	"""
	d = {'': 'MACHINE', 'name': p[2]}
	params = p[3]
	if params != None:
		d['()'] = params
	clauses = p[4]
	for cn,cv in clauses:
		assert cn not in d
		d[cn] = cv
	p[0] = d

def p_clause_machine_abstraite(p):
	"""clause_machine_abstraite : clause_constraints
 | clause_sees
 | clause_definitions
 | clause_includes
 | clause_promotes
 | clause_extends
 | clause_uses
 | clause_sets
 | clause_concrete_constants
 | clause_abstract_constants
 | clause_properties
 | clause_concrete_variables
 | clause_abstract_variables
 | clause_invariant
 | clause_assertions
 | clause_initialisation
 | clause_local_operations
 | clause_operations
	"""
	p[0] = p[1]

def p_raffinement(p):
	"""raffinement : _REFINEMENT_ Ident Ident_PLUSComma_PAR_OPT clause_refines clause_raffinement_STAR _END_
	"""
	d = {'': 'REFINEMENT', 'name': p[2]}
	params = p[3]
	if params != None:
		d['()'] = params
	cn,cv = p[4]
	d[cn] = cv
	clauses = p[5]
	for cn,cv in clauses:
		assert cn not in d
		d[cn] = cv
	p[0] = d

def p_clause_raffinement(p):
	"""clause_raffinement : clause_machine_abstraite
	"""
	p[0] = p[1]

def p_implantation(p):
	"""implantation : _IMPLEMENTATION_ Ident Ident_PLUSComma_PAR_OPT clause_refines clause_implantation_STAR _END_
	"""
	d = {'': 'IMPLEMENTATION', 'name': p[2]}
	params = p[3]
	if params != None:
		d['()'] = params
	cn,cv = p[4]
	d[cn] = cv
	clauses = p[5]
	for cn,cv in clauses:
		assert cn not in d
		d[cn] = cv
	p[0] = d

def p_clause_implantation(p):
	"""clause_implantation : clause_raffinement
 | clause_imports
 | clause_values
	"""
	p[0] = p[1]

def p_clause_constraints(p):
	"""clause_constraints : _CONSTRAINTS_ predicat
	"""
	p[0] = p[1:]

def p_clause_refines(p):
	"""clause_refines : _REFINES_ Ident
	"""
	p[0] = p[1:]

def p_clause_imports(p):
	"""clause_imports : _IMPORTS_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_sees(p):
	"""clause_sees : _SEES_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_includes(p):
	"""clause_includes : _INCLUDES_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_promotes(p):
	"""clause_promotes : _PROMOTES_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_extends(p):
	"""clause_extends : _EXTENDS_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_uses(p):
	"""clause_uses : _USES_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_sets(p):
	"""clause_sets : _SETS_ expr_PLUSSemicolon
	"""
	p[0] = p[1:]

def p_clause_concrete_constants(p):
	"""clause_concrete_constants : _CONCRETE_CONSTANTS_ Ident_PLUSComma
 | _CONSTANTS_ Ident_PLUSComma
	"""
	p[0] = ['CONCRETE_CONSTANTS', p[2]]

def p_clause_abstract_constants(p):
	"""clause_abstract_constants : _ABSTRACT_CONSTANTS_ Ident_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_properties(p):
	"""clause_properties : _PROPERTIES_ predicat
	"""
	p[0] = p[1:]

def p_clause_values(p):
	"""clause_values : _VALUES_ expr_PLUSSemicolon
	"""
	p[0] = p[1:]

def p_clause_concrete_variables(p):
	"""clause_concrete_variables : _CONCRETE_VARIABLES_ expr_PLUSComma
	"""
	p[0] = p[1:]

def p_clause_abstract_variables(p):
	"""clause_abstract_variables : _ABSTRACT_VARIABLES_ expr_PLUSComma
        | _VARIABLES_ expr_PLUSComma
        | _VISIBLE_VARIABLES_ expr_PLUSComma
	"""
	p[0] = ['ABSTRACT_VARIABLES', p[2]]

def p_clause_definitions(p):
	"""clause_definitions : _DEFINITIONS_ expr_PLUSSemicolon
	"""
	p[0] = p[1:]

def p_clause_invariant(p):
	"""clause_invariant : _INVARIANT_ predicat
	"""
	p[0] = [p[1], expr_split(p[2],'&')]

def p_clause_assertions(p):
	"""clause_assertions : _ASSERTIONS_ expr_PLUSSemicolon
	"""
	p[0] = p[1:]

def p_clause_initialisation(p):
	"""clause_initialisation : _INITIALISATION_ substitution
	"""
	p[0] = p[1:]

def p_clause_local_operations(p):
	"""clause_local_operations : _LOCAL_OPERATIONS_
 | _LOCAL_OPERATIONS_ expr_PLUSSemicolon
	"""
	ol = [] if len(p) == 2 else p[2]
	p[0] = [p[1] , get_operations(ol)]

def p_clause_operations(p):
	"""clause_operations : _OPERATIONS_
 | _OPERATIONS_ expr_PLUSSemicolon
	"""
	ol = [] if len(p) == 2 else p[2]
	p[0] = [p[1] , get_operations(ol)]

def p_condition(p):
	"""condition : expression
	"""
	p[0] = p[1]

def p_predicat(p):
	"""predicat : expression
	"""
	p[0] = p[1]

def p_substitution(p):
	"""substitution : expression
	"""
	p[0] = p[1]

def p_substitution_constr(p):
	"""substitution_constr : _skip_
 | _BEGIN_ substitution _END_
 | _PRE_ predicat _THEN_ substitution _END_
 | _ASSERT_ predicat _THEN_ substitution _END_
 | _IF_ predicat _THEN_ substitution _END_
 | _IF_ predicat _THEN_ substitution _ELSE_ substitution _END_
 | _IF_ predicat _THEN_ substitution ELSIF_part
 | _CHOICE_ substitution OR_substitution_PLUS _END_
 | _SELECT_ predicat _THEN_ substitution _END_
 | _SELECT_ predicat _THEN_ substitution _ELSE_ substitution _END_
 | _SELECT_ predicat _THEN_ substitution WHEN_part
 | _CASE_ expression _OF_ _EITHER_ expression _THEN_ substitution _END_ _END_
 | _CASE_ expression _OF_ _EITHER_ expression _THEN_ substitution _ELSE_ substitution _END_ _END_
 | _CASE_ expression _OF_ _EITHER_ expression _THEN_ substitution OR_THEN_part
 | _ANY_ Ident_PLUSComma _WHERE_ predicat _THEN_ substitution _END_
 | _LET_ Ident_PLUSComma _BE_ predicat _IN_ substitution _END_
 | _VAR_ Ident_PLUSComma _IN_ substitution _END_
 | _WHILE_ condition _DO_ substitution _INVARIANT_ predicat _VARIANT_ expression _END_
	"""
	k = p[1]
	if k == 'skip':
		p[0] = p[1]
	elif k == 'BEGIN':
		p[0] = p[1:3]
	elif k in ('PRE','ASSERT','VAR'):
		p[0] = [p[1], p[2], p[4]]
	elif k in ('IF', 'SELECT'):
		if len(p) == 6: # cas 1 et 3
			p[0] = [p[1], [p[2], p[4]] + ([] if p[5]=='END' else p[5]) ]
		elif len(p) == 8: # cas 2
			p[0] = [p[1], [[p[2], p[4]],[None,p[6]]] ]
		else:
			assert False
	elif k == 'CHOICE':
		p[0] = p[1:4]
	elif k == 'CASE':
		if len(p) in (9,10): # cas 1 et 3
			p[0] = [p[1], p[2], [p[5], p[7]] + ([] if p[8]=='END' else p[8]) ]
		elif len(p) == 12: # cas 2
			p[0] = [p[1], p[2], [[p[5], p[7]],[None,p[9]]] ]
		else:
			assert False
	elif k in ('ANY','LET'):
		p[0] = [p[1], p[2], p[4], p[6]]
	elif k == 'WHILE':
		p[0] = [p[1], p[2], p[4], p[6], p[8]]
	else:
		assert False, k

def p_ELSIF_part(p): ### retourne une liste de paires (pred,subst)
	"""ELSIF_part : _ELSIF_ predicat _THEN_ substitution _END_
 | _ELSIF_ predicat _THEN_ substitution _ELSE_ substitution _END_
 | _ELSIF_ predicat _THEN_ substitution ELSIF_part
	"""
	if len(p) == 6: # cas 1 et 3
		p[0] = [p[2], p[4]] + ([] if p[5]=='END' else p[5])
	elif len(p) == 8: # cas 2
		p[0] = [[p[2], p[4]],[None,p[6]]]
	else:
		assert False

def p_WHEN_part(p): ### retourne une liste de paires (pred,subst)
	"""WHEN_part : _WHEN_ predicat _THEN_ substitution _END_
 | _WHEN_ predicat _THEN_ substitution _ELSE_ substitution _END_
 | _WHEN_ predicat _THEN_ substitution WHEN_part
	"""
	if len(p) == 6: # cas 1 et 3
		p[0] = [p[2], p[4]] + ([] if p[5]=='END' else p[5])
	elif len(p) == 8: # cas 2
		p[0] = [[p[2], p[4]],[None,p[6]]]
	else:
		assert False

def p_OR_THEN_part(p):
	"""OR_THEN_part : _OR_ expression _THEN_ substitution _END_ _END_
 | _OR_ expression _THEN_ substitution _ELSE_ substitution _END_ _END_
 | _OR_ expression _THEN_ substitution OR_THEN_part
	"""
	if len(p) in (6,7): # cas 1 et 3
		p[0] = [p[2], p[4]] + ([] if p[5]=='END' else p[5])
	elif len(p) == 8: # cas 2
		p[0] = [[p[2], p[4]],[None,p[6]]]
	else:
		assert False

def p_expression_base(p): # Op11l = '[]'
	"""expression_base : Entier_litteral
	| DecimalFloat
 | Chaine_lit
 | Ident_ren
 |  '(' expression  ')'
 | InfSup
 |  '{'  '}'
 |  '{' expression  '}'
 |  '['  ']'
 |  Op11l
 |  '[' expression  ']'
  |  '[' expression  ']' Ident
 |  '?'
	"""
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 3:
		p[0] = '[]' if p[1] == '[' else '{}'
	elif len(p) == 4:
		p[0] = p[1:3]
	else:
		assert len(p) == 5
		p[0] = ['[]',p[2],p[4]]

def p_expression(p):
	"""expression : ex10
	"""
	p[0] = p[1]

def p_Ident_ren(p):
	"""Ident_ren : Ident
 | Ident_DOT
	"""
	p[0] = p[1]

def p_Chaine_lit(p):
	"""Chaine_lit : StringLit
	"""
	p[0] = p[1]

def p_Ident(p):
	"""Ident : Identifier
	"""
	p[0] = p[1]

def p_Ident_OPTDollar(p):
	"""Ident_OPTDollar : Ident
	| Ident '$' DecimalInt
	"""
	p[0] = p[1] if len(p)==2 else ['$',p[1],p[3]]

def p_Liste_Ident_OPTDollar(p):
	"""Liste_Ident_OPTDollar : Ident_OPTDollar
	| '(' Ident_OPTDollar_PLUSComma ')'
	"""
	p[0] = [p[1]] if len(p)==2 else p[2]

def p_Ident_DOT(p):
	"""Ident_DOT : Identifier_DOT
	"""
	p[0] = p[1]

def p_Entier_litteral(p):
	"""Entier_litteral : DecimalInt
	"""
	p[0] = p[1]

def p_clause_implantation_STAR(p):
	"""clause_implantation_STAR : 
 | clause_implantation clause_implantation_STAR
	"""
	make_seq_rr(p)

def p_clause_machine_abstraite_STAR(p):
	"""clause_machine_abstraite_STAR : 
 | clause_machine_abstraite clause_machine_abstraite_STAR
	"""
	make_seq_rr(p)

def p_clause_raffinement_STAR(p):
	"""clause_raffinement_STAR : 
 | clause_raffinement clause_raffinement_STAR
	"""
	make_seq_rr(p)

def p_expr_PLUSComma(p):
	"""expr_PLUSComma : expr_no_Comma
 | expr_no_Comma  ',' expr_PLUSComma
	"""
	make_seq_rr(p)

def p_expr_PLUSSemicolon(p):
	"""expr_PLUSSemicolon : expr_no_Semicolon
 | expr_no_Semicolon ';' expr_PLUSSemicolon
	"""
	make_seq_rr(p)

def p_Ident_PLUSComma(p):
	"""Ident_PLUSComma : Ident
 | Ident  ',' Ident_PLUSComma
	"""
	make_seq_rr(p)
	
def p_Ident_OPTDollar_PLUSComma(p):
	"""Ident_OPTDollar_PLUSComma : Ident_OPTDollar
 | Ident_OPTDollar  ',' Ident_OPTDollar_PLUSComma
	"""
	make_seq_rr(p)

def p_Ident_PLUSComma_PAR_OPT(p):
	"""Ident_PLUSComma_PAR_OPT : 
 |  '(' Ident_PLUSComma  ')'
	"""
	p[0] = p[2] if len(p) >=3 else None

def p_OR_substitution_PLUS(p):
	"""OR_substitution_PLUS : _OR_ substitution
 | _OR_ substitution OR_substitution_PLUS
	"""
	if len(p) == 3:
		p[0] = [p[2]]
	else:
		p[0] = [p[2]]+p[3]

def p_theory(p):
	"""theory : _THEORY_ Ident _END_
 | _THEORY_ Ident _IS_ expr_PLUSSemicolon _END_
	"""
	if len(p) == 4:
		p[0] = p[1:3] + [[]]
	else:
		p[0] = p[1:3] + [p[4]]

def p_ex10(p):
	"""ex10 : ex10 '|' ex11
 | ex11
	"""
	# ex10 : ex10 Op10l ex11
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex11(p): ## Op11l remplace par '[' ']' genere un S/R
	"""ex11 : ex11 Op11l ex20
 | ex20
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex20(p):
	"""ex20 : ex20  ';' ex20a
 | ex20a
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_expr_no_Semicolon(p):
	"""expr_no_Semicolon : ex20a
	"""
	p[0] = p[1]

def p_ex20a(p):
	"""ex20a : ex20b
	"""
	# ex20a : ex20b DblEqu ex20b
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex20b(p):
	"""ex20b : ex20b Op20l ex30
 | ex20b DblBar ex30
 | ex30
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex30(p):
	"""ex30 : ex30 Op30l ex40
 | ex30 EquSup ex40
 | ex40
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex40(p):
	"""ex40 : ex40 Op40l ex60
 | ex40 _or_ ex60
 | ex40 '&' ex60
 | ex60
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex60(p):
	"""ex60 : ex60 Op60l ex110
 | ex60 DblColon ex110
 | ex60 InfEquSup ex110
 | ex60 ':' ex110
 | ex60 '=' ex110
 | ex110
	"""
	# Op60l contient '\\'
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex110(p):
	"""ex110 : ex110 Op110l ex115
 | ex110 ColonEqu ex115
 | ex110 InfDblMinus ex115
 | ex115
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex115(p):
	"""ex115 : ex115  ',' ex120
 | ex120
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex120(p):
	"""ex120 : ex120 Op120l ex125
 | ex120 DblEqu ex125
 | ex125
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex125(p):
	"""ex125 : ex125 Op125l ex160
 | ex160
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_expr_no_Comma(p):
	"""expr_no_Comma : ex120
	"""
	p[0] = p[1]

def p_ex160(p):
	"""ex160 : ex160 Op160l ex170
 | ex160 '<' ex170
 | ex160 '>' ex170
 | ex160 '^' ex170
 | ex170
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex170(p):
	"""ex170 : ex170 Op170l ex180
 | ex170 DblDot ex180
 | ex180
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex180(p):
	"""ex180 : ex180 Op180l ex190
 | ex180 '-' ex190
 | ex180 '+' ex190
 | ex190
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex190(p):
	"""ex190 : ex190 Op190l ex200
 | ex190 '/' ex200
 | ex190 '*' ex200
 | ex190 _mod_ ex200
 | ex200
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex200(p):
	"""ex200 : ex210 Op200r ex200
 | ex210
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex210(p):
	"""ex210 : Op210 ex220
 | '-' ex220
 | _not_ ex220
 | ex220
	"""
	p[0] = p[1:3] if len(p) == 3 else p[1]

def p_ex220(p):
	"""ex220 : ex230 Op220r ex220
 | ex230
	"""
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_ex230(p):
	"""ex230 : ex230  '[' ex10  ']'
 | ex230a
	"""
	#  | ex230 '$' ex999
	#  | ex230  '(' ex10  ')'
	# ex230 : ex230 '~'
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 3:
		p[0] = [p[2],p[1]]
	else:
		p[0] = [p[2],p[1],p[3]]

def p_ex230a(p):
	"""ex230a : ex250
	"""
	# ex230a : ex250 Dot ex230a
	p[0] = [p[2], p[1], p[3]] if len(p) == 4 else p[1]

def p_Quantifier(p):
	"""Quantifier : "!"
	| "#"
	| "%"
	| "@"
	| _INTER_
	| _PI_
	| _SIGMA_
	| _UNION_
	| _SET_
	"""
	## new : SET
	p[0] = p[1]

def p_ex250(p):
	"""ex250 : ex250 Op250l ex300
 | ex250 "'" ex300
  | ex250  '(' ex10  ')'
  | ex250 '~'
 | ex300
	"""
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 3:
		p[0] = p[1:3]
	else:
		p[0] = [p[2],p[1],p[3]]

def p_ex300(p):
	"""ex300 : Quantifier Liste_Ident_OPTDollar Dot ex300
	| "!" Identifier_DOT '(' ex10 ')'
	| ex999
	"""
	#### !z.not(P & Q)
	p[0] = p[1]

def p_ex999(p):
	"""ex999 : expression_base
 | substitution_constr
 | theory
   | Identifier '$' DecimalInt
	"""
	p[0] = p[1]

#############################################
# Error rule for syntax errors
def p_error(p):
	# p est un ply.lex.LexToke,
	print('Syntax error at token ' + str(p))
	print('parser.symstack : ' + str(parser.symstack))
	print('parser.statestack : ' + str(parser.statestack))
	assert False

parser = yacc.yacc(optimize=0)
# ply2yacc.yacc(optimize=0)

if __name__ == '__main__':
	s = """
	2+2
	"""
	r = parser.parse(s, lexer = lexer)
	print(r)
