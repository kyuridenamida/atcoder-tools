from typing import Dict, Any

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult


def generate_template_parameters(prediction_result: FormatPredictionResult,
                                 constants: ProblemConstantSet,
                                 config: CodeStyleConfig) -> Dict[str, Any]:
    return {}

