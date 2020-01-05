#!/usr/bin/python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum


class NoJudgeTypeException(Exception):
    pass


class JudgeType(Enum):
    Normal = "normal"
    Decimal = "decimal"
    MultiSolution = "multisolution"
    Interactive = "interactive"


class ErrorType(Enum):
    Absolute = "absolute"
    Relative = "relative"
    AbsoluteOrRelative = "absolute_or_relative"


class Judge(metaclass=ABCMeta):
    @property
    @abstractmethod
    def judge_type(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass


class NormalJudge(Judge):
    judge_type = JudgeType.Normal

    def __init__(self):
        pass

    def verify(self, output, expected):
        return output == expected

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value,
        }

    @classmethod
    def from_dict(cls, dic):
        r = NormalJudge()
        return r


DEFAULT_EPS = 0.000000001


class DecimalJudge(Judge):
    judge_type = JudgeType.Decimal

    def __init__(self,
                 error_type: ErrorType = ErrorType.AbsoluteOrRelative,
                 diff: float = DEFAULT_EPS
                 ):
        self.judge_type = JudgeType.Decimal
        self.error_type = error_type
        self.diff = diff

    def _verify_sub(self, output: float, expected: float) -> bool:
        if self.error_type in [ErrorType.Absolute, ErrorType.AbsoluteOrRelative] and abs(
                expected - output) <= self.diff:
            return True
        if self.error_type in [ErrorType.Relative, ErrorType.AbsoluteOrRelative] and self._calc_absolute(output,
                                                                                                         expected):
            return True
        return False

    def _calc_absolute(self, output: float, expected: float) -> bool:
        if expected == 0:
            return expected == output
        return abs((expected - output) / expected) <= self.diff

    def verify(self, output, expected) -> bool:
        output = output.strip().split()
        expected = expected.strip().split()
        if len(output) != len(expected):
            return False
        for i in range(0, len(expected)):
            try:
                f = float(expected[i])
                if not self._verify_sub(float(output[i]), f):
                    return False
            except ValueError:
                if output[i] != expected[i]:
                    return False
        return True

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value,
            "error_type": self.error_type.value,
            "diff": self.diff
        }

    @classmethod
    def from_dict(cls, dic):
        r = DecimalJudge(
            diff=dic["diff"]
        )
        r.error_type = ErrorType(dic["error_type"])
        return r


class MultiSolutionJudge(Judge):
    judge_type = JudgeType.MultiSolution

    def __init__(self):
        pass

    def verify(self, output, expected):
        raise NotImplementedError()

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value
        }


class InteractiveJudge(Judge):
    judge_type = JudgeType.Interactive

    def verify(self, output, expected):
        raise NotImplementedError()

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value
        }
