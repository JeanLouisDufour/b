# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:59:50 2019

@author: F074018
"""

def expr_split(e, op=','):
	""
	if isinstance(e,list) and e[0] == op:
		[_, fst, snd] = e
		r = expr_split(fst,op) + expr_split(snd,op)
	else:
		r = [e]
	return r
