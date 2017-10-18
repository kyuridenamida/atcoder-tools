
class CalcParseError(Exception):
    pass


class EvaluteError(Exception):
    pass


class UnknownOperatorError(Exception):
    pass


def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def div(a, b):
    return a // b


def operator_to_string(operator):
    if operator == add:
        return "+"
    elif operator == sub:
        return "-"
    elif operator == mul:
        return "*"
    elif operator == div:
        return "/"
    else:
        raise UnknownOperatorError


class CalcNode:

    def __init__(self, formula=None):
        if formula:
            root = parse_to_calc_node(formula)
            self.content = root.content
            self.lch = root.lch
            self.rch = root.rch
            self.operator = root.operator
        else:
            self.content = None
            self.operator = None
            self.lch = None
            self.rch = None

    def __str__(self, depth=0):
        if self.operator is not None:
            lv = self.lch.__str__(depth=depth + 1)
            rv = self.rch.__str__(depth=depth + 1)
            res = "%s%s%s" % (lv, operator_to_string(self.operator), rv)
            if depth > 0 and (self.operator == add or self.operator == sub):
                res = "(%s)" % res
            return res
        elif isinstance(self.content, int):
            return str(self.content)
        else:
            return self.content

    def get_all_varnames(self):
        if self.operator is not None:
            lv = self.lch.get_all_varnames()
            rv = self.rch.get_all_varnames()
            return lv + rv
        elif isinstance(self.content, int):
            return []
        else:
            return [self.content]

    def evaluate(self, variables=None):
        if variables is None:
            variables = {}
        if self.operator is not None:
            lv = self.lch.evaluate(variables)
            rv = self.rch.evaluate(variables)
            return self.operator(lv, rv)
        elif isinstance(self.content, int):
            return int(self.content)
        else:
            if self.content not in variables:
                raise EvaluteError
            else:
                return variables[self.content]


def expr(formula, pos):
    res, pos = term(formula, pos)
    while formula[pos] == '+' or formula[pos] == '-':
        tmp = CalcNode()
        tmp.operator = add if formula[pos] == '+' else sub
        pos += 1
        tmp.lch = res
        tmp.rch, pos = term(formula, pos)
        res = tmp
    return res, pos


def term(formula, pos):
    res, pos = factor(formula, pos)
    while formula[pos] == '*' or formula[pos] == '/':
        tmp = CalcNode()
        tmp.operator = mul if formula[pos] == '*' else div
        pos += 1
        tmp.lch = res
        tmp.rch, pos = factor(formula, pos)
        res = tmp
    return res, pos


def factor(formula, pos):
    if formula[pos] == '(':
        pos += 1
        res, pos = expr(formula, pos)
        if formula[pos] != ')':
            raise CalcParseError
        pos += 1
        return res, pos
    elif formula[pos].isalpha():
        varname = ""
        while formula[pos].isalpha() or formula[pos] == '_':
            varname += formula[pos]
            pos += 1
        res = CalcNode()
        res.content = varname
        return res, pos
    elif formula[pos].isdigit() or formula[pos] == '-':
        if formula[pos] == '-':
            sign = -1
            pos += 1
            if not formula[pos].isdigit():
                raise CalcParseError
        else:
            sign = +1
        value = 0
        while formula[pos].isdigit():
            value = 10 * value + int(formula[pos])
            pos += 1
        value *= sign

        if formula[pos].isalpha() or formula[pos] == '(':
            # pattern like "123A"
            tmp = CalcNode()
            tmp.content = value
            res = CalcNode()
            res.lch = tmp
            res.rch, pos = factor(formula, pos)
            res.operator = mul
            return res, pos
        else:
            res = CalcNode()
            res.content = value
            return res, pos
    else:
        raise CalcParseError


def parse_to_calc_node(formula):
    """
            入力
                    formula # str : 式
            出力
                    #CalcNode : 構文木の根ノード

    """
    res, pos = expr(formula + "$", 0)  # $は使わないことにする
    if pos != len(formula):
        raise CalcParseError
    return res

if __name__ == '__main__':

    print(CalcNode("N-1-1+1000*N*N").evaluate({"N": 10}))
