import glob, os
import b_lexer as bl

src = r'E:\papa\mbd\b\livraison_officielle_04080951\b\src'
src = r'F:\AB\FreeRTOS_1.0\bdp'

bl.init_def_files(src)

for root, dirs, files in os.walk(src):
	for fn in files:
		if fn.endswith(('.mch','.ref','.imp','.pmi','.pmm','.po')):
			# if fn != 'FreeRTOSBasic.pmi': continue
			fp = os.path.join(root,fn)
			print('*******************************************')
			print(fp)
			fd = open(fp)
			prg = fd.read()
			fd.close()
			bl.lexer.input(prg)
			for t in bl.lexer: print(t)
			