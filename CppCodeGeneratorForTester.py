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



namespace SimpleInputchecker{
    istream *is = NULL;
    // void ensure(bool x){ if( !x ) throw 0; }
    #define ensure assert
    string readWord(int a,int b){
        auto is_c = [&](char c){
            if( c >= 'A' and c <= 'Z' ) return true;
            if( c >= 'a' and c <= 'z' ) return true;
            if( c >= '0' and c <= '9' ) return true;
            if( c == '-' ) return true;
            if( c == '_' ) return true;
            return false;
        };
        string w = "";
        while(is_c(is->peek())){
            w += is->get();
        }
        ensure(1 <= w.size() and w.size() <= b);
        return w;
    }
    void readSpace(){
        char x = is->get();
        ensure(x == ' ');
    }
    void readEndl(){
        char x = is->get();
        ensure(x == '\\n');
    }
    void readEof(){
        char x = is->get();
        ensure(x == char_traits<char>::eof());
    }
    long long readInt(long long a,long long b){
        
        const int maxlen = 19; // |input| < 10^18
        string w = readWord(1,maxlen);
        int sign = 1;
        if( w[0] == '-' ){
            ensure(w.size() >= 2 );
            ensure(w[1] != '0'); // -0 is invalid
            w = w.substr(1);
            sign = -1;
        }
        ensure(!(w.size() >= 2 and w[0] == '0'));
        long long ans = 0;
        for( auto c : w ){
            ensure(c >= '0' and c <= '9');
            ensure( ans <= 922337203685477580ll ); // =(2^63-1)/10
            ans = ans * 10 + c - '0';
        }
        ans *= sign;
        ensure( a <= ans and ans <= b);
        return ans;
    }
    void init(istream *set_is = &cin){
        is = set_is;
    }
    istream *create_mock_stream(string content){
        return new istringstream(content);
    }
    void test(){
        auto tmp_is = is;
        auto is1 = create_mock_stream("123 -123 abc\\n");
        create_mock_stream("123 -123 abc\\n");
        init(is1);
        ensure(readInt(1,123)==123);
        readSpace();
        ensure(readInt(-123,-123)==-123);
        readSpace();
        ensure(readWord(1,3)=="abc");
        readEndl();
        readEof();
        is = tmp_is;
    }
}
using namespace SimpleInputchecker;

void solve(%s){
    
}



int main(){    
    ios::sync_with_stdio(false);
    init(&cin);
    %s
    solve(%s);
    readEof();
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
    return "    " * n


sep_mapping_dic = {' ':'readSpace()','\n':'readEndl()',None:'// fail to put sep'}
input_mapping_dic = {int:'readInt()',float:'readDouble()',str:'readWord()'}

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
            lines.append(tab(depth+1) + "if( %s != %s ) %s; " % (loopv,str(node.index.zero_indexed().max_index),sep_mapping_dic[node.sep]) )
            lines.append(tab(depth) + "}")
            lines.append(tab(depth) + sep_mapping_dic[node.terminal_sep] + ";")
    else:
        lines.append(tab(depth) + "%s%s = %s;" % (node.varname,
                                                    "" if indexes == [] else "[" + "][".join(indexes) + "]",input_mapping_dic[var_information[node.varname].type]))
        if indexes == []:
            lines.append(tab(depth) + sep_mapping_dic[node.terminal_sep] + ";")
            
            #print(str(var_information[node.varname].type))
        
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
