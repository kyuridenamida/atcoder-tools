from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult
from atcodertools.fmtprediction.predict_simple_format import SimpleFormatPredictionFailedError, predict_simple_format
from atcodertools.fmtprediction.predict_types import TypePredictionFailedError, predict_types
from atcodertools.fmtprediction.tokenize_format import NoFormatFoundError, search_formats_with_minimum_vars


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):
    def __init__(self, cands: list[FormatPredictionResult]) -> None:
        self.cands = cands


def predict_format(content: ProblemContent) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()
    if input_format is None or samples is None:
        raise NoPredictionResultError

    if len(samples) == 0:
        raise NoPredictionResultError

    try:
        tokenized_possible_formats = search_formats_with_minimum_vars(input_format)
    except NoFormatFoundError as e:
        raise NoPredictionResultError from e

    output_cands = []
    for format in tokenized_possible_formats:
        for to_1d_flag in [False, True]:
            try:
                simple_format = predict_simple_format(format.var_tokens, to_1d_flag)
                output_cands.append(
                    FormatPredictionResult.create_typed_format(simple_format, predict_types(simple_format, samples))
                )
                break
            except (TypePredictionFailedError, SimpleFormatPredictionFailedError):
                pass

    if len(output_cands) > 1:
        raise MultiplePredictionResultsError(output_cands)
    if len(output_cands) == 0:
        raise NoPredictionResultError
    return output_cands[0]
