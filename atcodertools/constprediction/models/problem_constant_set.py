from atcodertools.common.judgetype import Judge


class ProblemConstantSet:

    def __init__(self,
                 mod: int = None,
                 yes_str: str = None,
                 no_str: str = None,
                 judge_method: Judge = None,
                 timeout: float = None,
                 is_format_analysis_allowed_by_rule: bool = None,
                 ):
        self.mod = mod
        self.yes_str = yes_str
        self.no_str = no_str
        self.judge_method = judge_method
        self.timeout = timeout
        self.is_format_analysis_allowed_by_rule = is_format_analysis_allowed_by_rule
