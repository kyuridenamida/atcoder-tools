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
    pass


class NormalJudge(Judge):
    def __init__(self):
        self.judge_type = JudgeType.Normal

    def verify(self, out, ans):
        return out == ans

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

    def verify_sub(self, out, ans: float) -> bool:
        if self.error_type in [ErrorType.Absolute, ErrorType.AbsoluteOrRelative] and abs(ans - out) <= self.diff:
            return True
        if self.error_type in [ErrorType.Relative, ErrorType.AbsoluteOrRelative] and abs((ans - out) / ans) <= self.diff:
            return True
        return False

    def verify(self, out, ans) -> bool:
        out = out.strip().split()
        ans = ans.strip().split()
        if len(out) != len(ans):
            return False
        for i in range(0, len(out)):
            if not self.verify_sub(float(out[i]), float(ans[i])):
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
    pass
