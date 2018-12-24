from atcodertools.models.predictor.format_prediction_result import FormatPredictionResult

from abc import ABC, abstractmethod


class CodeGenerator(ABC):

    @abstractmethod
    def generate_code(self, prediction_result: FormatPredictionResult):
        raise NotImplementedError


class NoPredictionResultGiven(Exception):
    pass
