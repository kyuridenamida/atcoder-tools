#!/usr/bin/python3
# -*- coding: utf-8 -*-

from AtCoder import AtCoder,SampleParseError
from utils import fixed_variable_name, devide_consecutive_vars, normalize_index
import AccountInformation
import FormatAnalyzer
import FormatTokenizer
import sys

def convert_to_cpptype_string(vtype):
	if( vtype == float ):
		return "long double"
	elif vtype == int:
		return "long long"
	elif vtype == str:
		return "string"
	else:
		raise NotImplementedError


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
		res += tab + type_template_before % (convert_to_cpptype_string(type_dic[k][1])) + " " + fixed_variable_name(k) + type_template_after + ";\n"
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
		lst.append(type_template_before % (convert_to_cpptype_string(type_dic[k][1])) + " " + fixed_variable_name(k))
		lst2.append(fixed_variable_name(k))
	formal_params = ", ".join(lst)
	real_params = ", ".join(lst2)
	return formal_params,real_params


def cpp_input(self,depth=1,index=[]):
	type(self.varname)
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
		res += tab + "cin >> %s%s;\n" % (fixed_variable_name(self.varname),"" if index == [] else "["+index[0]+"]")
	return res

FormatAnalyzer.FormatNode.cpp_source_gen = cpp_source_gen
FormatAnalyzer.FormatNode.cpp_definition = cpp_definition
FormatAnalyzer.FormatNode.cpp_solve_func = cpp_solve_func
FormatAnalyzer.FormatNode.cpp_input = cpp_input



import FormatTokenizer
import FormatAnalyzer

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def is_noise(s):
	return s == ":" or s == "...." or s == "..." or s == ".." or s == "."


def hoge(format,samples):
	#print(format)
	
	format = format.replace("\n"," ").replace("…"," ").replace("..."," ").replace(".."," ").replace("\ "," ").replace("}","} ").replace("　"," ")
	format = devide_consecutive_vars(format)
	format = normalize_index(format)
	format = format.replace("{","").replace("}","")
	tokens = [x for x in format.split(" ") if x != "" and is_ascii(x) and not is_noise(x)];
	#print(tokens)


	for candidate_format in FormatTokenizer.get_all_format_probabilities(tokens):
		#print(candidate_format)
		res,value_info = FormatAnalyzer.format_analyse(candidate_format)
		#print(res)
		
		try:
			current_dic = {}
			for sample in samples:
				sample = sample[0].replace("\n"," ")
				tokens = [x for x in sample.split(" ") if x != ""]
				current_dic = res.verifyAndGetTypes(tokens,current_dic)
			#print(res.cpp_source_gen(current_dic,value_info))
			return True

		except:
			pass
	return False


if __name__ == "__main__":
	
	atcoder = AtCoder(AccountInformation.username,AccountInformation.password)
	#informat,samples = atcoder.get_all("http://abc025.contest.atcoder.jp/tasks/abc025_c")
	#ys.exit(-1)
	succ = fail = 0


	for i in range(1,50):
		plist = atcoder.get_problem_list("arc%03d"%i)
		
		for k,v in plist.items():
			try:
				informat,samples = atcoder.get_all(v)
				if not hoge(informat,samples):
					raise Exception

				print("succ",v)
				succ += 1
				#sys.exit(-1)
			except KeyboardInterrupt:
				sys.exit(-1)
			except Exception as e:
				# print('=== エラー内容 ===')
				# print('type:' + str(type(e)))
				# print('e自身:' + str(e))
				# print("fail,",v)
				# pass
				fail += 1
		if(succ+fail>0):
			print (1.*succ/(succ+fail));
	# for i in range(1,35):
	# 	plist = atcoder.get_problem_list("abc%03d"%i)
		
	# 	for k,v in plist.items():
	# 		try:
	# 			informat,samples = atcoder.get_all(v)
	# 			if not hoge(informat,samples):
	# 				raise Exception
	# 			print("succ",v)
	# 			succ += 1
			
	# 		except:
	# 			print("fail,",v)
	# 			pass
	# 			fail += 1
	# 	if(succ+fail>0):
	# 		print (1.*succ/(succ+fail));
