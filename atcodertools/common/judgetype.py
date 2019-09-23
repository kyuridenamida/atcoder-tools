#!/usr/bin/python3
# -*- coding: utf-8 -*-


class JudgeType:
    def __init__(self,
                 judge_type: str = "normal",
                 is_absolute: bool = False,
                 is_relative: bool = False,
                 diff: float = 0.0
                 ):
        self.judge_type = judge_type
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

    def to_dict(self):
        return {
            "judge_type": self.judge_type,
            "error_type": self.error_type,
            "diff": self.diff
        }

    @classmethod
    def from_dict(cls, dic):
        r = JudgeType(
            judge_type=dic["judge_type"],
            diff=dic["diff"]
        )
        r.error_type = dic["error_type"]
        return r
