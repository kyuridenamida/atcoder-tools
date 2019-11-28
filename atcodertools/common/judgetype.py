#!/usr/bin/python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum
import platform


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
    def __init__(self,
                 error_type: ErrorType = ErrorType.AbsoluteOrRelative,
                 diff: float = DEFAULT_EPS
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


def get_judge_filename():
    judge_code_filename = "judge"
    if platform.system() == "Windows":
        judge_exec_filename = "judge.exe"
    else:
        judge_exec_filename = "judge"
    return judge_code_filename, judge_exec_filename


class MultiSolutionJudge(Judge):
    def __init__(self, judge_code_lang="cpp"):
        self.judge_type = JudgeType.MultiSolution
        self.judge_code_filename, self.judge_exec_filename = get_judge_filename()

        from atcodertools.common.language import Language
        self.judge_code_lang = Language.from_name(judge_code_lang)

    def verify(self, output, expected):
        raise NotImplementedError()

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value,
            "judge_code_filename": self.judge_code_filename,
            "judge_exec_filename": self.judge_exec_filename,
            "judge_code_lang": "cpp"
        }

    @classmethod
    def from_dict(cls, dic):
        r = MultiSolutionJudge(dic["judge_code_lang"])
        return r


class InteractiveJudge(Judge):
    def __init__(self, judge_code_lang="cpp"):
        self.judge_type = JudgeType.Interactive
        self.judge_code_filename, self.judge_exec_filename = get_judge_filename()
        from atcodertools.common.language import Language
        self.judge_code_lang = Language.from_name(judge_code_lang)

    def verify(self, output, expected):
        raise NotImplementedError()

    def to_dict(self):
        return {
            "judge_type": self.judge_type.value,
            "judge_code_filename": self.judge_code_filename,
            "judge_exec_filename": self.judge_exec_filename,
            "judge_code_lang": "cpp"
        }

    @classmethod
    def from_dict(cls, dic):
        r = InteractiveJudge(dic["judge_code_lang"])
        return r
