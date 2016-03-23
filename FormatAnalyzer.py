import copy
from Calculator import calcNode
from collections import OrderedDict
from utils import is_int, is_float, fixed_variable_name

import re


class TypesUnmatchedError(Exception): pass
class ParseError(Exception): pass
class UpCastingError(Exception): pass
class NotImplementedError(Exception): pass

def upcast(frm,to):
	if frm == to:
		return frm
	if (frm == int and to == float) or (frm == float or to == int):
		return float
	raise UpCastingError


class FormatNode:
	def __init__(self,varname=None,pointers=None,index=None):
		self.varname = varname
		self.pointers = pointers
		self.index = index


	def verifyAndGetTypes(self,tokens,init_dic={}):
		value_dic = copy.deepcopy(init_dic)
		if self.simulate(tokens,value_dic) != len(tokens) :
			raise ParseError
		return value_dic


	def simulate(self,tokens,value_dic,pos=0):
		def checkAndReflesh(value_dic,varname,value):
			if is_int(value):
				value = int(value)
			elif is_float(value):
				value = float(value)

			if varname in value_dic:
				value_dic[varname] = (value,upcast(value_dic[varname][1],type(value)));
			else:
				value_dic[varname] = (value,type(value))

		if self.pointers != None:
			if self.index == None :
				for child in self.pointers :
					pos = child.simulate(tokens,value_dic,pos)
				return pos
			else:
				def converted_dictionary(value_dic):
					dic = {}
					for k,v in value_dic.items():
						dic[k] = v[0]
					return dic
				minv = self.index.minVal.evaluate(converted_dictionary(value_dic))
				maxv = self.index.maxVal.evaluate(converted_dictionary(value_dic))
				for _ in range(minv,maxv+1):
					for child in self.pointers :
						pos = child.simulate(tokens,value_dic,pos)
				return pos
		else:
			checkAndReflesh(value_dic,self.varname,tokens[pos])
			pos += 1
			return pos

	def __str__(self):
		res = ""
		if self.pointers != None:
			if self.index != None :
				res += "(%s<=i<=%s)*" % (str(self.index.minVal),str(self.index.maxVal))
			res += "[" + " ".join([child.__str__() for child in self.pointers]) + "]"
		else:
			res = fixed_variable_name(self.varname)
		return res




class Index:
	def __init__(self):
		self.maxVal = calcNode("-1000000000000000000")
		# print(self.maxVal)
		self.minVal = calcNode("1000000000000000000")
		# print(self.minVal)
	def reflesh_min(self,v):
		if v.isdigit():
			if self.minVal.evaluate() > calcNode(v).evaluate():
				self.minVal = calcNode(v)
	def reflesh_max(self,v):
		if v.isdigit():
			if self.maxVal.evaluate() < calcNode(v).evaluate():
				self.maxVal = calcNode(v)
		else:
			self.maxVal = calcNode(v)

class VarInfo:
	def __init__(self,idxsize):
		self.appearances = []
		self.indexes = [Index() for _ in range(idxsize)] 

def format_analyse(parsed_tokens):

	'''
		入力
			parsed_tokens # list(list(str)) : 変数毎の変数名/インデックスがtokenizedなトークンリスト
		出力
			res,dic # FormatNode,OrderedDict<str:VarInfo> : フォーマット情報のノードと変数の情報を保持した辞書を同時に返す
	'''

	dic = OrderedDict()
	pos = 0

	#出現位置とかインデックスとしての最小値・最大値をメモ
	for token in parsed_tokens:
		idxs = token[1:]
		varname = token[0]
		if varname not in dic:
			dic[varname] = VarInfo(len(idxs))

		dic[varname].appearances.append(pos)
		print(idxs)
		for i,idx in enumerate(idxs):
			print(idxs)
			dic[varname].indexes[i].reflesh_min(idx)
			dic[varname].indexes[i].reflesh_max(idx)
		pos += 1

	#フォーマットノードの構築
	used = set()
	root = FormatNode(pointers=[])
	for i in range(len(parsed_tokens)):
		varname = parsed_tokens[i][0]
		idxs = parsed_tokens[i][1:]
		
		if varname in used:
			continue

		if len(dic[varname].appearances) != 1:
			# assume it's a arithmetic sequence
			span = dic[varname].appearances[1] - dic[varname].appearances[0]
			zipped_varnames = [token[0] for token in parsed_tokens[i:i+span]]
			for vname in zipped_varnames:
				used.add(vname)
			root.pointers.append( 
				FormatNode(pointers=[FormatNode(varname=vname) for vname in zipped_varnames],
					 index=dic[varname].indexes[0]
				)
			)
		else:
			root.pointers.append(FormatNode(varname))
			used.add(varname)

	return root,dic