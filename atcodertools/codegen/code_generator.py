from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult

from abc import ABC, abstractmethod


class CodeGenerator(ABC):

    @abstractmethod
    def generate_code(self, prediction_result: FormatPredictionResult, constants: ProblemConstantSet):
        raise NotImplementedError


class NoPredictionResultGiven(Exception):
    pass
