import json

from atcodertools.client.models.problem import Problem
from atcodertools.common.judgetype import NormalJudge, DecimalJudge, MultiSolutionJudge, InteractiveJudge, Judge, NoJudgeTypeException
from atcodertools.common.language import Language


DEFAULT_IN_EXAMPLE_PATTERN = 'in_*.txt'
DEFAULT_OUT_EXAMPLE_PATTERN = "out_*.txt"


class Metadata:

    def __init__(self, problem: Problem, code_filename: str, sample_in_pattern: str, sample_out_pattern: str,
                 lang: Language, judge_method: Judge = NormalJudge()):
        self.problem = problem
        self.code_filename = code_filename
        self.sample_in_pattern = sample_in_pattern
        self.sample_out_pattern = sample_out_pattern
        self.lang = lang
        self.judge_method = judge_method

    def to_dict(self):
        return {
            "problem": self.problem.to_dict(),
            "code_filename": self.code_filename,
            "sample_in_pattern": self.sample_in_pattern,
            "sample_out_pattern": self.sample_out_pattern,
            "lang": self.lang.name,
            "judge": self.judge_method.to_dict(),
        }

    @classmethod
    def from_dict(cls, dic):
        if "judge" in dic:
            judge_type = dic["judge"]["judge_type"]
            if judge_type == "normal":
                judge_method = NormalJudge.from_dict(dic["judge"])
            elif judge_type == "decimal":
                judge_method = DecimalJudge.from_dict(dic["judge"])
            elif judge_type == "multisolution":
                judge_method = MultiSolutionJudge.from_dict(dic["judge"])
            elif judge_type == "interactive":
                judge_method = InteractiveJudge.from_dict(dic["judge"])
            else:
                raise NoJudgeTypeException()
        else:
            judge_method = NormalJudge()

        return Metadata(
            problem=Problem.from_dict(dic["problem"]),
            code_filename=dic["code_filename"],
            sample_in_pattern=dic["sample_in_pattern"],
            sample_out_pattern=dic["sample_out_pattern"],
            lang=Language.from_name(dic["lang"]),
            judge_method=judge_method
        )

    def default_metadata():
        return Metadata(
            problem=None,
            code_filename="main.cpp",
            sample_in_pattern=DEFAULT_IN_EXAMPLE_PATTERN,
            sample_out_pattern=DEFAULT_OUT_EXAMPLE_PATTERN,
            lang=Language.from_name("cpp"),
            judge_method=NormalJudge()
        )

    @classmethod
    def load_from(cls, filename):
        with open(filename) as f:
            return cls.from_dict(json.load(f))

    def save_to(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=1, sort_keys=True)
            f.write('\n')
