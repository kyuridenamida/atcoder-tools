from typing import List

from core.AtCoderClient import ProblemContent
from core.FormatAnalyzer import analyze_format, FormatAnalysisFailedError
from core.FormatTokenizer import FormatTokenizer, NoFormatFoundError
from core.TypePredictor import type_predictor, TypePredictionFailedError
from core.models.predictor.FormatPredictionResult import FormatPredictionResult


class FormatPredictor:
    @staticmethod
    def predict(content: ProblemContent):
        input_format = content.get_input_format()
        samples = content.get_samples()

        if len(samples) == 0:
            raise NoPredictionResultError

        try:
            format_cands = FormatTokenizer(input_format).compute_formats_with_minimal_vars()
        except NoFormatFoundError:
            raise NoPredictionResultError


        output_cands = []
        for format in format_cands:
            for to_1d_flag in [False, True]:
                try:
                    fmt = analyze_format(format.var_tokens, to_1d_flag)
                    output_cands.append(FormatPredictionResult(fmt, type_predictor(fmt, samples)))
                    break
                except (TypePredictionFailedError, FormatAnalysisFailedError):
                    pass

        if len(output_cands) > 1:
            raise MultiplePredictionResultsError(output_cands)
        if len(output_cands) == 0:
            raise NoPredictionResultError
        return output_cands[0]


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):
    def __init__(self, cands):
        self.cands = cands
