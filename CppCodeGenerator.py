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

template = \
'''
#include <bits/stdc++.h>
using namespace std;

void solve(%s){
	
}

int main(){
	%s
	%s
	solve(%s);
	return 0;
}
'''
def code_generator(predict_result):
	formal_params,real_params = generate_params(predict_result.var_information)
	declaration_code = "\n\t".join(generate_declaration(predict_result.var_information))
	input_code = "\n\t".join(generate_inputpart(predict_result.analyzed_root))

	code = template % (formal_params, declaration_code, input_code, real_params)
	return code

def generate_declaration(var_information):
	lines = []
	for name,v in var_information.items():
		type_template_before = ""
		type_template_after = ""
		if len(v.indexes) == 1:
			type_template_before = "vector<%s>";
			type_template_after  = "("+str(v.indexes[0].zero_indexed().max_index)+"+1)"
		elif len(v.indexes) == 0:
			type_template_before = "%s";
			type_template_after  = ""
		elif len(v.indexes) == 2:
			type_template_before = "vector<vector<%s>>";
			type_template_after  = "("+str(v.indexes[0].zero_indexed().max_index)+"+1,vector<%s>("+str(v.indexes[1].zero_indexed().max_index)+"+1))"
		else:
			raise NotImplementedError

		line = type_template_before % (convert_to_cpptype_string(v.type)) + " " + name
		if len(v.indexes) == 2:
			line += type_template_after % (convert_to_cpptype_string(v.type))
		else:
			line += type_template_after
		line += ";"
		lines.append(line)
	return lines


def generate_params(var_information):
	lst = []
	lst2 = []
	for name,v in var_information.items():
		type_template_before = ""
		type_template_after = ""
		
		if len(v.indexes) == 1:
			type_template_before = "vector<%s>";
		elif len(v.indexes) == 0:
			type_template_before = "%s";
		elif len(v.indexes) == 2:
			type_template_before = "vector<vector<%s>>";
		else:
			raise NotImplementedError
		lst.append(type_template_before % (convert_to_cpptype_string(v.type)) + " " + name)
		lst2.append(name)
	formal_params = ", ".join(lst)
	real_params = ", ".join(lst2)
	return formal_params,real_params

def tab(n):
	return "	" * n

def generate_inputpart(node,depth=-1,indexes=[]):
	lines = []
	if node.pointers != None:
		if node.index != None :
			loopv = "i" if indexes == [] else "j"
			lines.append(tab(depth) + "for(int %s = %s ; %s <= %s ; %s++){" % (loopv,str(node.index.zero_indexed().min_index),loopv,str(node.index.zero_indexed().max_index),loopv))
			indexes = indexes + [loopv]
		for child in node.pointers:
			lines += generate_inputpart(child,depth+1,indexes)
		if node.index != None :
			lines.append(tab(depth) + "};")
	else:
		lines.append(tab(depth) + "cin >> %s%s;" % (node.varname, "" if indexes == [] else "["+"][".join(indexes)+"]"))
	return lines



if __name__ == "__main__":
	import AccountInformation
	from AtCoder import AtCoder
	import FormatPredictor	
	if len(sys.argv) == 3:
		contestid = sys.argv[1]
		pid = sys.argv[2]
		atcoder = AtCoder(AccountInformation.username,AccountInformation.password)
		plist = atcoder.get_problem_list(contestid)
		information,samples = atcoder.get_all(plist[pid])
		
		result = FormatPredictor.format_predictor(information,samples)
		if not result:
			raise Exception
		print(code_generator(result))
	else:
		print("# of argvs must be 2 (contestid(ex:arc001) and problemid(ex:A)).")

