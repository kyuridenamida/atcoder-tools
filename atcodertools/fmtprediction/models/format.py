from typing import List, TypeVar, Generic, Dict
from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.variable import Variable, SimpleVariable


class WrongGroupingError(Exception):
    pass


T = TypeVar('T', bound=SimpleVariable)  # T must be Variable or SimpleVariable


class Pattern(Generic[T]):

    def all_vars(self) -> List[T]:
        raise NotImplementedError

    def with_replaced_vars(self, name_to_var: Dict[str, Variable]) -> "Pattern[Variable]":
        raise NotImplementedError


class Format(Generic[T]):

    """
    Format without type information and separator information
    """

    def __init__(self) -> None:
        self.sequence: List[Pattern[T]] = []

    def push_back(self, pattern: Pattern[T]) -> None:
        self.sequence.append(pattern)

    def __str__(self) -> str:
        return "[{}]".format(",".join([str(c) for c in self.sequence]))

    def all_vars(self) -> List[T]:
        res: List[T] = []
        for seq in self.sequence:
            res += seq.all_vars()
        return res


class SingularPattern(Pattern[T]):

    """
    N
    """

    def __init__(self, var: T) -> None:
        self.var = var

    def __str__(self) -> str:
        return "(Singular: {})".format(self.var.name)

    def all_vars(self) -> List[T]:
        return [self.var]

    def with_replaced_vars(self, name_to_var: Dict[str, Variable]) -> "SingularPattern[Variable]":
        return SingularPattern(name_to_var[self.var.name])


class TwoDimensionalPattern(Pattern[T]):

    """
    a_1,1 ... a_1,w
    :
    a_h,1 ... a_h,w
    """

    def __init__(self, var: T) -> None:
        self.var = var

    def __str__(self) -> str:
        return "(TwoDimensional: {})".format(self.var.name)

    def all_vars(self) -> List[T]:
        return [self.var]

    def with_replaced_vars(self, name_to_var: Dict[str, Variable]) -> "TwoDimensionalPattern[Variable]":
        return TwoDimensionalPattern(name_to_var[self.var.name])


class ParallelPattern(Pattern[T]):

    """
    a1 a2 ... an

    or

    a1 b1 ... c1
    :
    an bn ... cn
    """

    def __init__(self, vars_: List[T]) -> None:
        self.vars = vars_
        self.loop_index = self._decide_loop_index(vars_)

    @staticmethod
    def _decide_loop_index(parallel_vars: List[T]) -> Index:
        first_var = parallel_vars[0]
        assert first_var.first_index is not None
        for var in parallel_vars:
            if var.dim_num() != 1:
                raise WrongGroupingError("dim_num must be 1")
            assert var.first_index is not None
            if var.first_index.min_index != first_var.first_index.min_index:
                raise WrongGroupingError(
                    "some pair of first indices has different min values")
            if var.first_index.max_index != first_var.first_index.max_index:
                raise WrongGroupingError(
                    "some pair of first indices has different max values")
        return first_var.first_index

    def __str__(self) -> str:
        return "(Parallel: {names} | {min} to {max})".format(
            names=",".join([str(c.name) for c in self.vars]),
            min=str(self.loop_index.min_index),
            max=str(self.loop_index.max_index)
        )

    def all_vars(self) -> List[T]:
        return self.vars

    def with_replaced_vars(self, name_to_var: Dict[str, Variable]) -> "ParallelPattern[Variable]":
        return ParallelPattern([name_to_var[var.name] for var in self.vars])
