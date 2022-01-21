from atcodertools.client.atcoder import ProblemContent
from atcodertools.fmtprediction.predict_simple_format import predict_simple_format, SimpleFormatPredictionFailedError
from atcodertools.fmtprediction.tokenize_format import NoFormatFoundError, \
    search_formats_with_minimum_vars
from atcodertools.fmtprediction.predict_types import predict_types, TypePredictionFailedError
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult
import re


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):

    def __init__(self, cands):
        self.cands = cands


def suspect_single_string(input_format: str, samples):
    a = input_format.strip().split()
    if len(a) != 1:
        return None
    input_format = a[0].strip()
    for sample in samples:
        s = sample.get_input().split()
        if len(s) != 1:
            return None
    i = input_format.find('_')
    if i == -1:
        return None
    pattern = input_format[0:i + 1]
    if len([m.start() for m in re.finditer(pattern, input_format)]) < 2:
        return None
    return input_format[0:i]


def predict_format(content: ProblemContent) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()
    input_format = input_format.replace('\'', 'prime')

    if len(samples) == 0:
        raise NoPredictionResultError

    for ct in [0, 1]:
        tokenized_possible_formats = []
        if ct == 0:
            try:
                tokenized_possible_formats += search_formats_with_minimum_vars(
                    input_format)
            except NoFormatFoundError:
                continue
        elif ct == 1:
            input_format2 = suspect_single_string(input_format, samples)
            if input_format2 is not None:
                try:
                    tokenized_possible_formats += search_formats_with_minimum_vars(
                        input_format2)
                except NoFormatFoundError:
                    raise NoPredictionResultError

        output_cands = []
        for format in tokenized_possible_formats:
            try:
                simple_format_array = predict_simple_format(format.var_tokens)
            except (TypePredictionFailedError, SimpleFormatPredictionFailedError):
                continue
            for simple_format in simple_format_array:
                try:
                    output_cands.append(
                        FormatPredictionResult.create_typed_format(simple_format, predict_types(simple_format, samples)))
                    break
                except (TypePredictionFailedError, SimpleFormatPredictionFailedError):
                    pass

        if len(output_cands) == 1:
            return output_cands[0]
        elif len(output_cands) > 1:
            raise MultiplePredictionResultsError(output_cands)
        elif ct == 0:
            continue
        else:
            raise NoPredictionResultError
