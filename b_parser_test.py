import codecs, glob, os
import b_parser as bp
import b_lexer as bl
from b_util import expr_split

def analyze_prj(prj):
	""
	assert os.path.exists(prj)
	src = os.path.join(prj,'src')
	if not os.path.exists(src):
		src = prj
	bdp = os.path.join(prj,'bdp')
	if not os.path.exists(bdp):
		bdp = os.path.join(prj,'pdb')
		assert os.path.exists(bdp)
	
	bl.init_def_files(src)

	src_d = {}
	for root, dirs, files in os.walk(src):
		for fn in files:
			if root==src and fn.endswith(('.mch','.ref','.imp')):
				fp = os.path.join(root,fn)
				print('*******************************')
				print(fp)
				fd = open(fp)
				prg = fd.read()
				fd.close()
				bl.lexer.lexobj.lineno = 1
				r = bp.parser.parse(prg, lexer = bl.lexer)
				if fn[:-4] not in src_d:
					src_d[fn[:-4]] = r
	
	for root, dirs, files in os.walk(bdp):
		for fn in files:
			if root==bdp and fn.endswith(('.pmi','.pmm','.po')):
				fp = os.path.join(root,fn)
				print('*******************************')
				print(fp)
				fd = open(fp)
				prg = fd.read()
				fd.close()
				bl.lexer.lexobj.lineno = 1
				r = bp.parser.parse(prg, lexer = bl.lexer)
				l = expr_split(r,'&')
				d = {}
				for th in l:
					assert th[0] == 'THEORY' and len(th)==3, th
					assert th[1].isidentifier() and th[1] not in d
					assert isinstance(th[2],list)
					d[th[1]] = th[2]
				if fn.endswith('.pmi'):
					mn = fn[:-4]
					mch = src_d[mn]
					mk = mch['']
					mops = mch.get('OPERATIONS', {})
					mlops = mch.get('LOCAL_OPERATIONS', {})
					# mops.add(mlops)
					assert {'BalanceX','MethodList','PassList','ProofState'} <= set(d) <= {'BalanceX','ManForms','MethodList','PassList','ProofState','Version'}, list(d)
					th_BalanceX = d['BalanceX']
					th_ProofState = d['ProofState']
					th_MethodList = d['MethodList']
					th_PassList = d['PassList']
					#
					bal = [expr_split(b,',') for b in th_BalanceX]
					bal0 = bal[0]
					assert bal0[0] == mn
					npo = bal0[1]
					assert len(th_ProofState) == len(th_MethodList) == len(th_PassList) == npo
					assert npo == sum(b[1] for b in bal[1:])
					print('nb po : {}'.format(npo))
					mch['BalanceX'] = [b[:2] for b in bal[1:]]
				elif fn.endswith('.po'):
					mn = fn[:-3]
					mch = src_d[mn]
					assert {'EnumerateX','Formulas','ProofList'} <= set(d) <= {'EnumerateX','Formulas','ProofList','Version'}, list(d)
					mch.update(d)
				else:
					pass
	
	for mn,mv in src_d.items():
		print('*********** {} *****************'.format(mn))
		th_BalanceX = mv.get('BalanceX',[])
		npo = sum(b[1] for b in th_BalanceX)
		th_ProofList = mv.get('ProofList',[])
		assert len(th_ProofList) == npo
		2+2
				
prj_l = [r'F:\AB\acses',
		 #r'E:\papa\mbd\b\livraison_officielle_04080951\b',
		 r'F:\AB\FreeRTOS_1.0',
		 r'F:\AB\FreeRTOS',
		 r'F:\AB\bbook_lift',
		 ]
_prj_l = [r'F:\AB\bbook_lift']

for prj in prj_l:
	analyze_prj(prj)
