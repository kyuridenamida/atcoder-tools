import copy
from Calculator import calcNode
from collections import OrderedDict
import Calculator
import re


def is_float(text):
	return re.match("-?\d+\.\d+$",text) != None

def is_int(text):
	return re.match("-?\d+$",text) != None

def is_ascii(s):
    return all(ord(c) < 128 for c in s)
def is_noise(s):
	return s == ":" or s == "...." or s == "..." or s == ".." or s == "."

def is_variable_name(name):
	return all( ('a' <= c and c <= 'z') or ('A' <=c and c <= 'Z') or c == '_' for c in name)

def is_description(desc):
	if desc[-1] == '-' :
		return False
	if desc.find('_') != -1 :
		return False
	return True

def fix_variable_name(name):
	if name[-1] == "_": return name[:-1]
	return name

def convert_to_cpptype_string(vtype):
	if( vtype == float ):
		return "long double"
	elif vtype == int:
		return "long long"
	elif vtype == str:
		return "string"
	else:
		raise NotImplementedError

finalAnswer = []

def deviding_pattern(text,vars):
	# 変数名に数字は含まれない　分割は3つまで考える
	candidate = [[text]]
	candidate += [[text[:i],text[i:]] for i in range(1,len(text))]
	for i in range(1,len(text)):
		for j in range(i+1,len(text)):
			candidate += [[text[:i],text[i:j],text[j:]]]

	res = []
	for c in candidate:
		flag = True
		if not is_variable_name(c[0]): 
			flag = False
		for desc in c[1:]:
			if not is_description(desc):
				flag = False
			if is_variable_name(desc) and desc not in vars:
				flag = False
		
		if c[0] in vars and vars[c[0]] != len(c):
			flag = False;

		if flag:
			res.append(c)
	# print(res)
	return res


def dfs(finalAnswer,tokens,currentState,pos,vars,lim):
	'''
		limの枝刈りのみで終了した場合はTrueが返ってくる
	'''
	if len(vars) > lim :
		return True
	if pos == len(tokens):
		finalAnswer.append(copy.deepcopy(currentState))
		return False
	flag = False
	for d in deviding_pattern(tokens[pos],vars):
		nextVars = copy.deepcopy(vars)
		nextVars[d[0]] = len(d)
		currentState.append(d)
		if dfs(finalAnswer,tokens,currentState,pos+1,nextVars,lim) :
			flag = True
		currentState.pop()
	return flag

def get_all_format_probabilities(tokens):
	finalAnswer = []
	lim = 1
	while len(finalAnswer) == 0:
		if not dfs(finalAnswer,tokens,[],0,{},lim):
			break
		lim += 1
		# print(lim)
	return finalAnswer

def is_arithmetic_sequence(seq):
	if len(seq) <= 1 :
		return True
	for i in range(1,len(seq)):
		if seq[1]-seq[0] != seq[i] - seq[i-1]:
			return False
	return True


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

class Node:
	def __init__(self,varname=None,pointers=None,index=None):
		self.varname = varname
		self.pointers = pointers
		self.index = index


	def verifyAndGetTypes(self,tokens,init_dic={}):
		value_dic = copy.deepcopy(init_dic)
		if self.simulate(tokens,value_dic) != len(tokens) :
			raise ParseError
		return value_dic



	def checkOrAppend(value_dic,varname,value):
		if is_int(value):
			value = int(value)
		elif is_float(value):
			value = float(value)

		if varname in value_dic:
			value_dic[varname] = (value,upcast(value_dic[varname][1],type(value)));
		else:
			value_dic[varname] = (value,type(value))

	def simulate(self,tokens,value_dic,pos=0):
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
				minv = Calculator.parseToNode(str(self.index.minVal)).evalute(converted_dictionary(value_dic))
				maxv = Calculator.parseToNode(str(self.index.maxVal)).evalute(converted_dictionary(value_dic))
				for _ in range(minv,maxv+1):
					for child in self.pointers :
						pos = child.simulate(tokens,value_dic,pos)
				return pos
		else:
			Node.checkOrAppend(value_dic,self.varname,tokens[pos])
			pos += 1
			return pos

	def cpp_source_gen(self,type_dic,value_info):
		formal_params,real_params = self.cpp_solve_func(type_dic,value_info)
		res = "#include <bits/stdc++.h>\n" \
			+ "using namespace std;\n" \
			+ "\n" \
			+ "void solve(%s){\n" % formal_params \
			+ "    \n" \
			+ "}\n" \
			+ "\n" \
			+ "int main(){\n" \
			+ self.cpp_definition(type_dic, value_info) \
			+ "\n" \
			+ self.cpp_input() \
			+ "    solve(%s);\n" % real_params \
			+ "}\n"
		return res



	def cpp_definition(self,type_dic,value_info):
		tab = "    ";
		res = ""
		for k,v in value_info.items():
			type_template_before = ""
			type_template_after = ""
			
			if len(v.indexes) == 1:
				type_template_before = "vector<%s>";
				type_template_after  = "("+str(v.indexes[0].maxVal)+"+1)"
			elif len(v.indexes) == 0:
				type_template_before = "%s";
				type_template_after  = ""
			else:
				raise NotImplementedError
			res += tab + type_template_before % (convert_to_cpptype_string(type_dic[k][1])) + " " + fix_variable_name(k) + type_template_after + ";\n"
		return res


	def cpp_solve_func(self,type_dic,value_info):
		res = ""
		lst = []
		lst2 = []
		for k,v in value_info.items():
			type_template_before = ""
			type_template_after = ""
			
			if len(v.indexes) == 1:
				type_template_before = "vector<%s>";
				type_template_after  = "("+str(v.indexes[0].maxVal)+"+1)"
			elif len(v.indexes) == 0:
				type_template_before = "%s";
				type_template_after  = ""
			else:
				raise NotImplementedError
			lst.append(type_template_before % (convert_to_cpptype_string(type_dic[k][1])) + " " + fix_variable_name(k))
			lst2.append(fix_variable_name(k))
		formal_params = ", ".join(lst)
		real_params = ", ".join(lst2)
		return formal_params,real_params


	def cpp_input(self,depth=1,index=[]):
		tab = "    " * (depth-1)
		res = ""
		if self.pointers != None:
			if self.index != None :
				res += tab + "for(int i = %s ; i <= %s ; i++){\n" % (str(self.index.minVal),str(self.index.maxVal))
				index = index + ["i"]
			for child in self.pointers:
				res += child.cpp_input(depth+1,index)
			if self.index != None :
				res += tab + "}\n"
		else:
			res += tab + "cin >> %s%s;\n" % (fix_variable_name(self.varname),"" if index == [] else "["+index[0]+"]")
		return res



	def __str__(self):
		res = ""
		if self.pointers != None:
			if self.index != None :
				res += "(%s<=i<=%s)*" % (str(self.index.minVal),str(self.index.maxVal))
			res += "[" + " ".join([child.__str__() for child in self.pointers]) + "]"
		else:
			res = fix_variable_name(self.varname)
		return res







def format_analyse(parsed_tokens):
	dic = OrderedDict()
	pos = 0
	class Index:
		def __init__(self):
			self.maxVal = -1000000000000000000
			self.minVal = +1000000000000000000
		def reflesh_min(self,v):
			if v.isdigit():
				self.minVal = min([int(v),self.minVal])
		def reflesh_max(self,v):
			if v.isdigit():
				self.maxVal = max([int(v),self.maxVal])
			else:
				self.maxVal = v

	class VarInfo:
		def __init__(self,idxsize):
			self.appearances = []
			self.indexes = [Index() for _ in range(idxsize)] 

	for token in parsed_tokens:
		idxs = token[1:]
		varname = token[0]
		if varname not in dic:
			dic[varname] = VarInfo(len(idxs))
		dic[varname].appearances.append(pos)
		for i,idx in zip(range(len(idxs)),idxs):
			dic[varname].indexes[i].reflesh_min(idx)
			dic[varname].indexes[i].reflesh_max(idx)
		pos += 1

	for k,v in dic.items():
		print(v.appearances)
		for idx in v.indexes:
			print(idx.minVal,idx.maxVal)
	


	used = set()
	root = Node(pointers=[])
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
				Node(pointers=[Node(varname=vname) for vname in zipped_varnames],
					 index=dic[varname].indexes[0]
				)
			)


		else:
			root.pointers.append(Node(varname))
			used.add(varname)

	return root,dic



def hoge(format,samples):
	format = format.replace("{","").replace("}"," ").replace("\n"," ").replace("…"," ").replace(",","").replace("\ "," ")

	tokens = [x for x in format.split(" ") if x != "" and is_ascii(x) and not is_noise(x)];
	print(tokens)

	for candidate_format in get_all_format_probabilities(tokens):
		res,value_info = format_analyse(candidate_format)
		print(res)
		current_dic = {}
		for sample in samples:
			sample = sample[0].replace("\n"," ")
			tokens = [x for x in sample.split(" ") if x != ""]
			current_dic = res.verifyAndGetTypes(tokens,current_dic)

		print(res.cpp_source_gen(current_dic,value_info))
