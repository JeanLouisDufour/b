import json, os
import b_parser as bp
import b_lexer as bl

class BB: # B Batch
	"""
	add_file/af file_name
	close_project/clp
	open_project/op proj_name
	pogenerate/po comp_name 1/0
	project_infos/ip proj_name
	typecheck/t comp_name
	"""
	pdb = '_b_'
	
	def __init__(self, chemin):
		""
		assert os.path.exists(chemin)
		self.chemin = chemin
		self.pdb_path = os.path.join(chemin, BB.pdb)
		if not os.path.exists(self.pdb_path):
			os.mkdir(self.pdb_path)
		self.pdb_file = os.path.join(self.pdb_path, BB.pdb+'.json')
		if not os.path.exists(self.pdb_file):
			self.pdb_content = {}
			self._write_pdb()
		else:
			self._read_pdb()
		bl.init_def_files(chemin)
	
	def _write_pdb(self):
		""
		with open(self.pdb_file,'w') as fd:
			json.dump(self.pdb_content, fd)
	
	def _read_pdb(self):
		""
		with open(self.pdb_file,'r') as fd:
			self.pdb_content = json.load(fd)
	
	def add_file(self, fn):
		""
		assert fn.endswith(('.mch','.ref','.imp'))
		fp = os.path.join(self.chemin, fn)
		assert os.path.exists(fp)
		assert fn not in self.pdb_content
		fd = open(fp)
		prg = fd.read()
		fd.close()
		bl.lexer.lexobj.lineno = 1
		r = bp.parser.parse(prg, lexer = bl.lexer)
		fp_json = os.path.join(self.pdb_path, fn+'.json')
		with open(fp_json,'w') as fd:
			json.dump(r,fd, indent='\t', sort_keys=True)
		
	def pogenerate(self, c_name):
		""
		assert c_name in self.pdb_content
		c_info = self.pdb_content[c_name]
		c_kind = c_info['']
		c_ext = '.mch'
		c_ast_path = os.path.join(self.pdb_path, c_name+c_ext+'.json')
		with open(c_ast_path,'r') as fd:
			c_ast = json.load(fd)
		c_INV = c_ast.get('INVARIANT')
		c_INI = c_ast.get('INITIALISATION')
		c_OPd = c_ast.get('OPERATIONS')
		for prop in c_INV:
			po = apply_subst(c_INI, prop)
			
		