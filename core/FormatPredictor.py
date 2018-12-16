from typing import List

from core.AtCoderClient import ProblemContent
from core.FormatAnalyzer import analyze_format
from core.FormatTokenizer import FormatTokenizer
from core.TypePredictor import type_predictor
from core.models.predictor.FormatPredictionResult import FormatPredictionResult


class FormatPredictor:
    @staticmethod
    def predict(content: ProblemContent):
        input_format = content.get_input_format()
        samples = content.get_samples()
        format_cands = FormatTokenizer(input_format).compute_formats_with_minimal_vars()

        for to_1d_flag in [False, True]:
            for format in format_cands:
                fmt = analyze_format(format.var_tokens, to_1d_flag)

                try:
                    print(type_predictor(fmt, samples))
                    return FormatPredictionResult(fmt, type_predictor(fmt, samples))
                except Exception as e:
                    print("error", e)
                    pass
        raise NoPredictionResultError


class NoPredictionResultError(Exception):
    pass
