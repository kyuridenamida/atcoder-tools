import json

from atcodertools.client.models.problem import Problem
from atcodertools.common.language import Language


class Metadata:

    def __init__(self, problem: Problem, code_filename: str, sample_in_pattern: str, sample_out_pattern: str, lang: Language):
        self.problem = problem
        self.code_filename = code_filename
        self.sample_in_pattern = sample_in_pattern
        self.sample_out_pattern = sample_out_pattern
        self.lang = lang

    def to_dict(self):
        return {
            "problem": self.problem.to_dict(),
            "code_filename": self.code_filename,
            "sample_in_pattern": self.sample_in_pattern,
            "sample_out_pattern": self.sample_out_pattern,
            "lang": self.lang.name,
        }

    @classmethod
    def from_dict(cls, dic):
        return Metadata(
            problem=Problem.from_dict(dic["problem"]),
            code_filename=dic["code_filename"],
            sample_in_pattern=dic["sample_in_pattern"],
            sample_out_pattern=dic["sample_out_pattern"],
            lang=Language.from_name(dic["lang"]),
        )

    @classmethod
    def load_from(cls, filename):
        with open(filename) as f:
            return cls.from_dict(json.load(f))

    def save_to(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=1, sort_keys=True)
