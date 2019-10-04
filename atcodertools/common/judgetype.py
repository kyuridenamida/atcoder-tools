#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum


class JudgeType(Enum):
    Normal = "normal"
    Decimal = "decimal"
    Other = "other"


class ErrorType(Enum):
    Absolute = "absolute"
    Relative = "relative"
    AbsoluteOrRelative = "absolute_or_relative"


class Judge:
    def verify(self, output, expected):
        pass


class NormalJudge(Judge):
    def __init__(self):
        self.judge_type = JudgeType.Normal

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


class DecimalJudge(Judge):
    def __init__(self,
                 error_type: ErrorType = ErrorType.AbsoluteOrRelative,
                 diff: float = 0.0
                 ):
        self.judge_type = JudgeType.Decimal
        self.error_type = error_type
        self.diff = diff

    def __verify_sub(self, output, expected: float) -> bool:
        if self.error_type in [ErrorType.Absolute, ErrorType.AbsoluteOrRelative] and abs(expected - output) <= self.diff:
            return True
        if self.error_type in [ErrorType.Relative, ErrorType.AbsoluteOrRelative] and abs((expected - output) / expected) <= self.diff:
            return True
        return False

    def verify(self, output, expected) -> bool:
        output = output.strip().split()
        expected = expected.strip().split()
        if len(output) != len(expected):
            return False
        for i in range(0, len(output)):
            if not self.__verify_sub(float(output[i]), float(expected[i])):
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
