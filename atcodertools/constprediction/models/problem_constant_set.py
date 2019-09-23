from atcodertools.common.judgetype import JudgeType


class ProblemConstantSet:

    def __init__(self,
                 mod: int = None,
                 yes_str: str = None,
                 no_str: str = None,
                 judge_type: JudgeType = None,
                 ):
        self.mod = mod
        self.yes_str = yes_str
        self.no_str = no_str
        self.judge_type = judge_type
