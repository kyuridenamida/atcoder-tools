from typing import Optional

from atcodertools.common.judgetype import Judge, NormalJudge


class ProblemConstantSet:
    def __init__(
        self,
        mod: Optional[int] = None,
        yes_str: Optional[str] = None,
        no_str: Optional[str] = None,
        judge_method: Optional[Judge] = None,
    ) -> None:
        self.mod = mod
        self.yes_str = yes_str
        self.no_str = no_str
        self.judge_method: Judge = judge_method if judge_method is not None else NormalJudge()
