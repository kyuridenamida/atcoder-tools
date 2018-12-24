from typing import List

from atcodertools.models.analyzer.analyzed_variable import AnalyzedVariable
from atcodertools.models.analyzer.index import Index


class WrongGroupingError(Exception):
    pass


class Pattern:

    def all_vars(self) -> List[AnalyzedVariable]:
        raise NotImplementedError


class SimpleFormat:

    """
    Format without type information and separator information
    """

    def __init__(self):
        self.sequence = []

    def push_back(self, pattern: Pattern):
        self.sequence.append(pattern)

    def __str__(self):
        return "[{}]".format(",".join([str(c) for c in self.sequence]))

    def all_vars(self):
        res = []
        for seq in self.sequence:
            res += seq.all_vars()
        return res


class SingularPattern(Pattern):

    """
    N
    """

    def __init__(self, var: AnalyzedVariable):
        self.var = var

    def __str__(self):
        return "(Singular: {})".format(self.var.var_name)

    def all_vars(self):
        return [self.var]


class TwoDimensionalPattern(Pattern):

    """
    a_1,1 ... a_1,w
    :
    a_h,1 ... a_h,w
    """

    def __init__(self, var: AnalyzedVariable):
        self.var = var

    def __str__(self):
        return "(TwoDimensional: {})".format(self.var.var_name)

    def all_vars(self):
        return [self.var]


class ParallelPattern(Pattern):

    """
    a1 a2 ... an

    or

    a1 b1 ... c1
    :
    an bn ... cn
    """

    def __init__(self, vars: List[AnalyzedVariable]):
        self.vars = vars
        self.loop_index = self._decide_loop_index(vars)

    @staticmethod
    def _decide_loop_index(parallel_vars: List[AnalyzedVariable]) -> Index:
        first_var = parallel_vars[0]
        for var in parallel_vars:
            if var.dim_num() != 1:
                raise WrongGroupingError("dim_num must be 1")
            if var.first_index.min_index != first_var.first_index.min_index:
                raise WrongGroupingError(
                    "some pair of first indices has different min values")
            if var.first_index.max_index != first_var.first_index.max_index:
                raise WrongGroupingError(
                    "some pair of first indices has different max values")
        return first_var.first_index

    def __str__(self):
        return "(Parallel: {names} | {min} to {max})".format(
            names=",".join([str(c.var_name) for c in self.vars]),
            min=str(self.loop_index.min_index),
            max=str(self.loop_index.max_index)
        )

    def all_vars(self):
        return self.vars
