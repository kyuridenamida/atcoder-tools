#!/usr/bin/python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum


class JudgeType(Enum):
    Normal = "normal"
    Decimal = "decimal"
    Other = "other"


class ErrorType(Enum):
    Absolute = "absolute"
    Relative = "relative"
    AbsoluteOrRelative = "absolute_or_relative"


DEFAULT_EPS = 1e-9


class NoJudgeTypeException(Exception):
    pass


def _normalize_output(text: str):
    """
    Split text into lines for comparison.

    Trailing whitespace of each line and trailing empty lines are
    ignored so that the result matches AtCoder's judge behavior,
    where e.g. "a b " and "a b" are both accepted.
    """
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


class Judge(metaclass=ABCMeta):
    @abstractmethod
    def verify(self, output, expected):
        pass

    @abstractmethod
    def to_dict(self):
        pass


class NormalJudge(Judge):
    def __init__(self):
        self.judge_type = JudgeType.Normal

    def verify(self, output, expected):
        return _normalize_output(output) == _normalize_output(expected)

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value,
        }

    @classmethod
    def from_dict(cls, dic):
        r = NormalJudge()
        return r


class DecimalJudge(Judge):
    def __init__(self,
                 error_type: ErrorType = ErrorType.AbsoluteOrRelative,
                 diff: float = 0.0
                 ):
        self.judge_type = JudgeType.Decimal
        self.error_type = error_type
        self.diff = diff

    def _verify_sub(self, output: float, expected: float) -> bool:
        if self.error_type in [ErrorType.Absolute, ErrorType.AbsoluteOrRelative] and abs(expected - output) <= self.diff:
            return True
        if self.error_type in [ErrorType.Relative, ErrorType.AbsoluteOrRelative] and self._calc_absolute(output, expected):
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
        for i in range(0, len(output)):
            if not self._verify_sub(float(output[i]), float(expected[i])):
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


class OtherJudge(Judge):
    # dummy
    pass


class JudgeMethod:
    """A plain data holder describing a judge method.

    ProblemConstantSet keeps this instead of a Judge subclass so that
    code-generation templates can read judge settings (type, error type,
    diff) as simple attributes. Convert to a Judge via to_judge() when
    the verification behavior is needed (e.g. in tester)."""

    def __init__(self,
                 judge_type: JudgeType = JudgeType.Normal,
                 error_type: ErrorType = None,
                 diff: float = None):
        self.judge_type = judge_type
        self.error_type = error_type
        self.diff = diff

    def to_judge(self) -> Judge:
        if self.judge_type == JudgeType.Decimal:
            return DecimalJudge(
                error_type=self.error_type or ErrorType.AbsoluteOrRelative,
                diff=self.diff if self.diff is not None else 0.0)
        return NormalJudge()
