import copy
from Calculator import CalcNode
from collections import OrderedDict
from utils import is_int, is_float, fixed_variable_name
import re


class TypesUnmatchedError(Exception):
    pass


class ParseError(Exception):
    pass


class UpCastingError(Exception):
    pass


def upcast(frm, to):
    if frm == to:
        return frm
    if (frm == int and to == float) or (frm == float or to == int):
        return float
    raise UpCastingError


class Index:
    def __init__(self):
        self.max_index = None
        self.min_index = None

    def reflesh_min(self, v):
        if v.isdigit():
            if self.min_index is None or self.min_index.evaluate() > CalcNode(v).evaluate():
                self.min_index = CalcNode(v)

    def reflesh_max(self, v):
        if v.isdigit():
            if self.max_index is None or (
                            self.max_index.get_all_varnames() == [] and self.max_index.evaluate() < CalcNode(
                        v).evaluate()):
                self.max_index = CalcNode(v)
        else:
            self.max_index = CalcNode(v)

    def zero_indexed(self):
        res = Index()
        res.min_index = CalcNode("0")
        res.max_index = CalcNode(
            str(self.max_index) + "-(" + str(self.min_index) + ")")
        return res


class VariableInformation:
    def __init__(self, name, idxsize):
        self.name = name
        self.indexes = [Index() for _ in range(idxsize)]
        self.type = None


class FormatNode:
    def __init__(self, varname=None, pointers=None, index=None):
        self.varname = varname
        self.pointers = pointers
        self.index = index
        self.sep = None
        self.terminal_sep = None

    def verify_and_get_types(self, tokens, init_dic=None):
        if init_dic is None:
            init_dic = {}
        value_dic = copy.deepcopy(init_dic)
        if self.simulate(tokens, value_dic) != len(tokens):
            raise ParseError
        return value_dic

    def simulate(self, tokens, value_dic, pos=0):
        def check_and_reflesh(value_dic, varname, value):
            if is_int(value):
                value = int(value)
            elif is_float(value):
                value = float(value)

            if varname in value_dic:
                value_dic[varname] = (value, upcast(
                    value_dic[varname][1], type(value)))
            else:
                value_dic[varname] = (value, type(value))

        if self.pointers is not None:
            if self.index is None:
                for child in self.pointers:
                    pos = child.simulate(tokens, value_dic, pos)
                return pos
            else:
                def converted_dictionary(value_dic):
                    dic = {}
                    for k, v in value_dic.items():
                        dic[k] = v[0]
                    return dic

                minv = self.index.min_index.evaluate(
                    converted_dictionary(value_dic))
                maxv = self.index.max_index.evaluate(
                    converted_dictionary(value_dic))

                for _ in range(minv, maxv + 1):
                    for child in self.pointers:
                        pos = child.simulate(tokens, value_dic, pos)
                        if maxv - minv != 1 and self.sep is None:
                            self.sep = tokens[pos - 1][1]
                self.terminal_sep = tokens[pos - 1][1]
                return pos
        else:

            check_and_reflesh(value_dic, self.varname, tokens[pos][0])
            self.terminal_sep = tokens[pos][1]
            pos += 1
            return pos

    def __str__(self):
        res = ""
        if self.pointers is not None:
            if self.index is not None:
                res += "(%s<=i<=%s)*" % (str(self.index.min_index),
                                         str(self.index.max_index))
            res += "[" + " ".join([child.__str__()
                                   for child in self.pointers]) + "]"
        else:
            res = fixed_variable_name(self.varname)
        return res + "(sep:[" + str(ord(str(self.sep)[0])) + "] terminal_sep = [" + str(
            ord(str(self.terminal_sep)[0])) + "]" + ")"


def format_analyse(parsed_tokens, to_1d_flag=False):
    """
            入力
                    parsed_tokens # list(list(str)) : 変数毎の変数名/インデックスがtokenizedなトークンリスト
            出力
                    res,dic # FormatNode,OrderedDict<str:VariableInformation> : フォーマット情報のノードと変数の情報を保持した辞書を同時に返す
    """

    appearances = {}
    dic = OrderedDict()
    pos = 0

    # 出現位置とかインデックスとしての最小値・最大値をメモ
    for token in parsed_tokens:
        idxs = token[1:]
        varname = token[0]
        if varname not in dic:
            dic[varname] = VariableInformation(varname, len(idxs))
            appearances[varname] = []
        appearances[varname].append(pos)
        # print(idxs)
        for i, idx in enumerate(idxs):
            dic[varname].indexes[i].reflesh_min(idx)
            dic[varname].indexes[i].reflesh_max(idx)
        pos += 1

    # フォーマットノードの構築
    processed = set()
    root = FormatNode(pointers=[])
    for i in range(len(parsed_tokens)):
        varname = parsed_tokens[i][0]
        if varname in processed:
            continue

        dim = len(dic[varname].indexes)

        if dim == 2 and to_1d_flag:
            dic[varname].indexes = dic[varname].indexes[:-1]
            dim = 1
        if dim == 0:
            root.pointers.append(FormatNode(varname))
            processed.add(varname)
        elif dim == 1:
            if len(appearances[varname]) >= 2:
                # assume it's a arithmetic sequence
                span = appearances[varname][1] - appearances[varname][0]
            elif len(appearances[varname]) == 1:
                # or mono
                span = 1

            zipped_varnames = [token[0] for token in parsed_tokens[i:i + span]]
            for vname in zipped_varnames:
                processed.add(vname)
            root.pointers.append(
                FormatNode(pointers=[FormatNode(varname=vname) for vname in zipped_varnames],
                           index=dic[varname].indexes[0]
                           )
            )
        elif dim == 2:
            processed.add(varname)
            inner_node = FormatNode(pointers=[FormatNode(
                varname=varname)], index=dic[varname].indexes[1])
            root.pointers.append(FormatNode(
                pointers=[inner_node], index=dic[varname].indexes[0]))
        else:
            raise NotImplementedError

    return root, dic
