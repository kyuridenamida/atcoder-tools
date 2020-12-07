import itertools
import re
from typing import Dict


class CalcParseError(Exception):
    pass


class EvaluateError(Exception):
    pass


class UnknownOperatorError(Exception):
    pass


def add(a, b):
    try:
        return a + b
    except TypeError as e:
        raise EvaluateError(e)


def sub(a, b):
    try:
        return a - b
    except TypeError as e:
        raise EvaluateError(e)


def mul(a, b):
    try:
        return a * b
    except TypeError as e:
        raise EvaluateError(e)


def div(a, b):
    try:
        return a // b
    except TypeError as e:
        raise EvaluateError(e)


def _operator_to_string(operator):
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

    def __init__(self, content=None, operator=None, lch=None, rch=None):
        self.content = content
        self.lch = lch
        self.rch = rch
        self.operator = operator

    def is_operator_node(self):
        return self.operator is not None

    def is_constant_node(self):
        return isinstance(self.content, int)

    def is_variable_node(self):
        return not self.is_operator_node() and not self.is_constant_node()

    def __eq__(self, other):
        return self.__str__() == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self, depth=0):
        opens = []  # Position list of open brackets
        cands = []
        original_formula = self.to_string_strictly()
        for i, c in enumerate(original_formula):
            if c == '(':
                opens.append(i)
            elif c == ')':
                assert len(opens) > 0
                cands.append((opens[-1], i))
                opens.pop()
        pass

        values_for_identity_check = [3, 14, 15, 92]

        def likely_identical(formula: str):
            node = CalcNode.parse(formula)
            vars = node.get_all_variables()
            for combination in itertools.product(values_for_identity_check, repeat=len(vars)):
                val_dict = dict(zip(vars, list(combination)))
                if self.evaluate(val_dict) != node.evaluate(val_dict):
                    return False
            return True

        # Remove parentheses greedy
        res_formula = list(original_formula)
        for op, cl in cands:
            tmp = res_formula.copy()
            tmp[op] = ''
            tmp[cl] = ''
            if likely_identical("".join(tmp)):
                res_formula = tmp
        simplified_form = "".join(res_formula)

        return simplified_form

    def get_all_variables(self):
        if self.is_operator_node():
            lv = self.lch.get_all_variables()
            rv = self.rch.get_all_variables()
            return lv + rv
        elif self.is_constant_node():
            return []
        else:
            return [self.content]

    def evaluate(self, variables: Dict[str, int] = None):
        if variables is None:
            variables = {}
        if self.is_operator_node():
            lv = self.lch.evaluate(variables)
            rv = self.rch.evaluate(variables)
            return self.operator(lv, rv)
        elif self.is_constant_node():
            return int(self.content)
        else:
            if self.content not in variables:
                raise EvaluateError(
                    "Found an unknown variable '{}'".format(self.content))
            else:
                return variables[self.content]

    def simplify(self):
        current_formula = str(self)

        # Really stupid heuristics but covers the major case.
        while True:
            next_formula = re.sub(r"-1\+1$", "", current_formula)
            next_formula = re.sub(r"\+0$", "", next_formula)
            next_formula = re.sub(r"-0$", "", next_formula)
            next_formula = re.sub(r"[+-]0\+", "+", next_formula)
            if next_formula == current_formula:
                break
            current_formula = next_formula

        return CalcNode.parse(current_formula)

    def to_string_strictly(self):
        if self.is_operator_node():
            return "({lch}{op}{rch})".format(
                lch=self.lch.to_string_strictly(),
                op=_operator_to_string(self.operator),
                rch=self.rch.to_string_strictly()
            )
        else:
            return str(self.content)

    @classmethod
    def parse(cls, formula: str):
        res, pos = _expr(formula + "$", 0)  # $ is put as a terminal character
        if pos != len(formula):
            raise CalcParseError
        return res


def _expr(formula, pos):
    res, pos = _term(formula, pos)
    while formula[pos] == '+' or formula[pos] == '-':
        tmp = CalcNode()
        tmp.operator = add if formula[pos] == '+' else sub
        pos += 1
        tmp.lch = res
        tmp.rch, pos = _term(formula, pos)
        res = tmp
    return res, pos


def _term(formula, pos):
    res, pos = _factor(formula, pos)
    while formula[pos] == '*' or formula[pos] == '/':
        tmp = CalcNode()
        tmp.operator = mul if formula[pos] == '*' else div
        pos += 1
        tmp.lch = res
        tmp.rch, pos = _factor(formula, pos)
        res = tmp
    return res, pos


def _factor(formula, pos):
    if formula[pos] == '(':
        pos += 1
        res, pos = _expr(formula, pos)
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
            res.rch, pos = _factor(formula, pos)
            res.operator = mul
            return res, pos
        else:
            res = CalcNode()
            res.content = value
            return res, pos
    else:
        raise CalcParseError
