from src.models.predictor.FormatPredictionResult import FormatPredictionResult

from abc import ABC, abstractmethod


class CodeGenerator(ABC):
    @abstractmethod
    def generate_code(self, prediction_result: FormatPredictionResult):
        raise NotImplementedError


class NoPredictionResultGiven(Exception):
    pass
