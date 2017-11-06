import os

from functools import reduce
from core.TemplateEngine import render


mydir = os.path.dirname(__file__)


def tab(n):
    if n <= 0:
        return ""
    else:
        return "\t" * n


def indent(lines):
    return [tab(1) + line for line in lines]


def convert_to_javatype_string(vtype):
    '''
    :param vtype:
    :return: その型に対応するJavaにおける文字列表現
    '''
    if vtype == float:
        return "double"
    elif vtype == int:
        return "long"
    elif vtype == str:
        return "String"
    else:
        raise NotImplementedError


def input_code(vtype, vname_for_input):
    if vtype == float:
        return '{name} = sc.nextDouble()'.format(name=vname_for_input)
    elif vtype == int:
        return '{name} = sc.nextInt()'.format(name=vname_for_input)
    elif vtype == str:
        return '{name} = sc.next()'.format(name=vname_for_input)
    else:
        raise NotImplementedError


def generate_declaration(v):
    '''
    :param v: 変数情報
    :return: 変数vの宣言パートを作る ex) array[1..n] → int[] array = new int[n]
    '''

    dim = len(v.indexes)
    typename = convert_to_javatype_string(v.type)

    if dim == 0:
        type_template_before = "{type}".format(type=typename)
        type_template_after = ""
    elif dim == 1:
        type_template_before = "{type}[]".format(type=typename)
        type_template_after = " = new {type}[{size}+1]".format(type=typename,
                                                               size=v.indexes[0].zero_indexed().max_index)
    elif dim == 2:
        type_template_before = "{type}[][]".format(type=typename)
        type_template_after = " = new {type}[{row_size}+1][{col_size}+1)]".format(
            type=typename,
            row_size=v.indexes[0].zero_indexed().max_index,
            col_size=v.indexes[1].zero_indexed().max_index
        )
    else:
        raise NotImplementedError

    line = "{declaration} {name}{constructor};".format(
        name=v.name,
        declaration=type_template_before,
        constructor=type_template_after
    )
    return line


def generate_arguments(var_information):
    '''
    :param var_information: 全変数の情報
    :return: 仮引数、実引数の文字列表現(順序は両者同じ);
        - formal_params: 仮引数 ex) int a, string b, vector<int> ccc
        - actual_params : 実引数 ex) a, b, ccc
    '''
    formal_lst = []
    actual_lst = []
    for name, v in var_information.items():
        dim = len(v.indexes)
        typename = convert_to_javatype_string(v.type)

        if dim == 0:
            type_template = "{type}".format(type=typename)
        elif dim == 1:
            type_template = "{type}[]".format(type=typename)
        elif dim == 2:
            type_template = "{type}[][]".format(type=typename)
        else:
            raise NotImplementedError

        formal_lst.append("{type} {name}".format(
            type=type_template, name=name))
        actual_lst.append(name)
    formal_params = ", ".join(formal_lst)
    actual_params = ", ".join(actual_lst)
    return formal_params, actual_params


def generate_input_part(node, var_information, inputted, undeclared, depth, indexes):
    '''
    :param node: FormatPredictorで得られる解析結果の木(const)
    :param var_information: 変数の情報(const)
    :param inputted: 入力が完了した変数名集合 (呼ぶときはset())
    :param undeclared: 入力が完了していない変数名集合 (呼ぶときはset(現れる変数全部))
    :param depth: ネストの深さ (呼ぶときは0で呼ぶ)
    :param indexes: 二重ループで再帰してるとき、indexes=["i","j"]みたいな感じになってる。 (呼ぶときは[])
    :return: 入力コードの列
    '''
    lines = []

    def declare_if_ready():
        '''
            サブルーチンです。例えば
                K N a_1 ...a_N　
            という入力に対して、Nを代入する前に
                vector<int> a(N);
            を宣言してしまうと悲しいので、既に必要な変数が全て入力されたものから宣言していく。
        '''
        nonlocal lines, inputted, undeclared, var_information
        will_declare = []
        for vname in undeclared:
            related_vars = reduce(lambda a, b: a + b,
                                  [index.min_index.get_all_varnames() + index.max_index.get_all_varnames()
                                   for index in var_information[vname].indexes], []
                                  )
            if all([(var in inputted) for var in related_vars]):
                will_declare.append(vname)

        for vname in will_declare:
            lines.append(generate_declaration(var_information[vname]))
            undeclared.remove(vname)

    if depth == 0:
        # 入力の開始時、何の制約もない変数をまず全部宣言する (depth=-1 <=> 入力の開始)
        declare_if_ready()

    if node.pointers is not None:
        '''
            何かしらの塊を処理(インデックスを持っている場合はループ)
            [a,b,c] or [ai,bi,ci](min<=i<=max) みたいな感じ
        '''

        if node.index is None:
            for child in node.pointers:
                lines += generate_input_part(child, var_information,
                                             inputted, undeclared, depth + 1, indexes)
        else:
            loopv = "i" if indexes == [] else "j"

            # ループの開始
            lines.append("for(int {x} = {start} ; {x} <= {end} ; {x}++){{".format(
                x=loopv,
                start=node.index.zero_indexed().min_index,
                end=node.index.zero_indexed().max_index)
            )
            # ループの内側
            for child in node.pointers:
                lines += indent(generate_input_part(child, var_information,
                                                    inputted, undeclared, depth + 1, indexes + [loopv]))
            # ループの外
            if node.index is not None:
                lines.append("}")
    else:
        ''' 変数が最小単位まで分解されたときの入力処理 '''
        vname_for_input = node.varname + \
            ("" if indexes == [] else "[" + "][".join(indexes) + "]")
        vtype = var_information[node.varname].type

        line = "{input_code};".format(
            input_code=input_code(vtype, vname_for_input))
        lines.append(line)
        inputted.add(node.varname)

        declare_if_ready()

    return lines


def code_generator(predict_result=None):
    with open("{dir}/template_success.java".format(dir=mydir), "r") as f:
        template_success = f.read()
    with open("{dir}/template_failure.java".format(dir=mydir), "r") as f:
        template_failure = f.read()

    if predict_result is not None:
        formal_arguments, actual_arguments = generate_arguments(
            predict_result.var_information)
        input_part_lines = generate_input_part(
            node=predict_result.analyzed_root,
            var_information=predict_result.var_information,
            inputted=set(),
            undeclared=set(predict_result.var_information.keys()),
            depth=0,
            indexes=[]
        )

        code = render(template_success,
                      formal_arguments=formal_arguments,
                      actual_arguments=actual_arguments,
                      input_part=input_part_lines)
    else:
        code = template_failure
    return code
