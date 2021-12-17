from atcodertools.client.atcoder import ProblemContent
from atcodertools.fmtprediction.predict_simple_format import predict_simple_format, SimpleFormatPredictionFailedError
from atcodertools.fmtprediction.tokenize_format import NoFormatFoundError, \
    search_formats_with_minimum_vars
from atcodertools.fmtprediction.predict_types import predict_types, TypePredictionFailedError
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):

    def __init__(self, cands):
        self.cands = cands


def predict_format(content: ProblemContent) -> list[FormatPredictionResult]:
    input_format = content.get_input_format()
    samples = content.get_samples()

    if len(samples) == 0:
        raise NoPredictionResultError

    try:
        tokenized_possible_formats = search_formats_with_minimum_vars(
            input_format)
    except NoFormatFoundError:
        raise NoPredictionResultError

    output_cands = []
    for to_1d_flag in [False, True]:
        try:
            simple_format = []
            for a in tokenized_possible_formats:
                for format in a:
                    simple_format.append(predict_simple_format(format.var_tokens, to_1d_flag))
            output_cands.append(
                FormatPredictionResult.create_typed_format(simple_format, predict_types(simple_format, samples, input_format.loop_length_var)))
            break
        except (TypePredictionFailedError, SimpleFormatPredictionFailedError):
            pass

    if len(output_cands) > 1:
        raise MultiplePredictionResultsError(output_cands)
    if len(output_cands) == 0:
        raise NoPredictionResultError

    return output_cands[0]
