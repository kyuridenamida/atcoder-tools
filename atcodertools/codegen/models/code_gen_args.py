from typing import Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.fmtprediction.models.format import Format
from atcodertools.fmtprediction.models.variable import Variable


class CodeGenArgs:

    def __init__(self,
                 template: str,
                 format_: Optional[Format[Variable]],
                 constants: ProblemConstantSet,
                 config: CodeStyleConfig):
        self.template = template
        self.format = format_
        self.constants = constants
        self.config = config
