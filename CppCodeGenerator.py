from functools import reduce


def convert_to_cpptype_string(vtype):
    if(vtype == float):
        return "long double"
    elif vtype == int:
        return "long long"
    elif vtype == str:
        return "string"
    else:
        raise NotImplementedError

template_success = \
    '''#include <bits/stdc++.h>
using namespace std;

void solve(%s){
	
}



int main(){	
	ios::sync_with_stdio(false);
	%s
	solve(%s);
	return 0;
}
'''

template_failed = \
    '''// failed to generate code

#include <bits/stdc++.h>
using namespace std;

int main(){	
	ios::sync_with_stdio(false);
	
}
'''


def code_generator(predict_result=None):
    if predict_result is not None:
        formal_params, real_params = generate_params(
            predict_result.var_information)
        input_code = "\n\t".join(generate_inputpart(predict_result.analyzed_root,
                                                    predict_result.var_information, set(), set(predict_result.var_information.keys())))

        code = template_success % (formal_params, input_code, real_params)
    else:
        code = template_failed
    return code


def generate_declaration(v):
    type_template_before = ""
    type_template_after = ""
    if len(v.indexes) == 0:
        type_template_before = "%s"
        type_template_after = ""
    elif len(v.indexes) == 1:
        type_template_before = "vector<%s>"
        type_template_after = "(" + \
            str(v.indexes[0].zero_indexed().max_index) + "+1)"

    elif len(v.indexes) == 2:
        type_template_before = "vector<vector<%s>>"
        type_template_after = "(" + str(v.indexes[0].zero_indexed(
        ).max_index) + "+1,vector<%s>(" + str(v.indexes[1].zero_indexed().max_index) + "+1))"
    else:
        raise NotImplementedError

    line = type_template_before % (
        convert_to_cpptype_string(v.type)) + " " + v.name
    if len(v.indexes) == 2:
        line += type_template_after % (convert_to_cpptype_string(v.type))
    else:
        line += type_template_after
    line += ";"
    return line


def generate_params(var_information):
    lst = []
    lst2 = []
    for name, v in var_information.items():
        type_template_before = ""
        type_template_after = ""

        if len(v.indexes) == 1:
            type_template_before = "vector<%s>"
        elif len(v.indexes) == 0:
            type_template_before = "%s"
        elif len(v.indexes) == 2:
            type_template_before = "vector<vector<%s>>"
        else:
            raise NotImplementedError
        lst.append(type_template_before %
                   (convert_to_cpptype_string(v.type)) + " " + name)
        lst2.append(name)
    formal_params = ", ".join(lst)
    real_params = ", ".join(lst2)
    return formal_params, real_params


def tab(n):
    return "	" * n


def generate_inputpart(node, var_information, decided, ungenerated, depth=-1, indexes=[]):
    lines = []
    if depth == -1:
        cands = []
        for vname in ungenerated:
            related_vars = reduce(lambda a, b: a + b,
                                  [index.min_index.get_all_varnames() + index.max_index.get_all_varnames()
                                   for index in var_information[vname].indexes], []
                                  )
            if related_vars == []:
                cands.append(vname)

        for vname in cands:
            lines.append(generate_declaration(var_information[vname]))
            ungenerated.remove(vname)

    if node.pointers != None:
        if node.index != None:
            loopv = "i" if indexes == [] else "j"
            lines.append(tab(depth) + "for(int %s = %s ; %s <= %s ; %s++){" % (loopv, str(
                node.index.zero_indexed().min_index), loopv, str(node.index.zero_indexed().max_index), loopv))
            indexes = indexes + [loopv]
        for child in node.pointers:
            lines += generate_inputpart(child, var_information,
                                        decided, ungenerated, depth + 1, indexes)
        if node.index != None:
            lines.append(tab(depth) + "}")
    else:
        lines.append(tab(depth) + "cin >> %s%s;" % (node.varname,
                                                    "" if indexes == [] else "[" + "][".join(indexes) + "]"))
        decided.add(node.varname)

        cands = []
        for vname in ungenerated:
            related_vars = reduce(lambda a, b: a + b,
                                  [index.min_index.get_all_varnames() + index.max_index.get_all_varnames()
                                   for index in var_information[vname].indexes], []
                                  )
            if all([var in decided for var in related_vars]):
                cands.append(vname)

        for vname in cands:
            lines.append(generate_declaration(var_information[vname]))
            ungenerated.remove(vname)

    return lines
