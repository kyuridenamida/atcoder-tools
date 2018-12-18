import os
from core.TemplateEngine import render
from core.models.analyzer import AnalyzedVariable
from core.models.analyzer.SimpleFormat import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern
from core.models.predictor.FormatPredictionResult import FormatPredictionResult
from core.models.predictor.Variable import Variable

from abc import ABC, abstractmethod


class CodeGenerator(ABC):
    @abstractmethod
    def generate_code(self, template: str, prediction_result: FormatPredictionResult):
        pass


class NoPredictionResultGiven(Exception):
    pass
