from core.models.predictor.FormatPredictionResult import FormatPredictionResult

from abc import ABC, abstractmethod


class CodeGenerator(ABC):
    @abstractmethod
    def generate_code(self, template: str, prediction_result: FormatPredictionResult):
        pass


class NoPredictionResultGiven(Exception):
    pass
