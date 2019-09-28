#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum


class JudgeType(Enum):
    Normal = "normal"
    Decimal = "decimal"
    Other = "other"


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
                 is_absolute: bool = False,
                 is_relative: bool = False,
                 diff: float = 0.0
                 ):
        self.judge_type = JudgeType.Decimal
        if is_absolute:
            if is_relative:
                self.error_type = "absolute_or_relative"
            else:
                self.error_type = "absolute"
        else:
            if is_relative:
                self.error_type = "relative"
            else:
                self.error_type = None
        self.diff = diff

    def verify_sub(self, out, ans: float) -> bool:
        if self.error_type in ["absolute", "absolute_or_relative"] and abs(ans - out) <= self.diff:
            return True
        if self.error_type in ["relative", "absolute_or_relative"] and abs((ans - out) / ans) <= self.diff:
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
            "error_type": self.error_type,
            "diff": self.diff
        }

    @classmethod
    def from_dict(cls, dic):
        r = DecimalJudge(
            diff=dic["diff"]
        )
        r.error_type = dic["error_type"]
        return r


class OtherJudge(Judge):
    pass
