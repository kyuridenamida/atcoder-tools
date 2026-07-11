from atcodertools.client.atcoder import ProblemContent
from atcodertools.fmtprediction.models.format_prediction_result import (
    FormatPredictionResult,
)
from atcodertools.fmtprediction.predict_multi_case_format import (
    MultipleMultiCaseFormatsError,
    NoMultiCaseFormatFoundError,
    predict_multi_case_format,
)
from atcodertools.fmtprediction.predict_simple_format import (
    SimpleFormatPredictionFailedError,
    predict_simple_format,
)
from atcodertools.fmtprediction.predict_types import (
    TypePredictionFailedError,
    predict_types,
)
from atcodertools.fmtprediction.tokenize_format import (
    NoFormatFoundError,
    search_formats_with_minimum_vars,
)


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):
    def __init__(self, cands):
        self.cands = cands


def _predict_single_case(
    content: ProblemContent,
) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()

    try:
        tokenized_possible_formats = (
            search_formats_with_minimum_vars(
                input_format
            )
        )
    except NoFormatFoundError:
        raise NoPredictionResultError

    output_cands = []

    for tokenized_format in tokenized_possible_formats:
        for to_1d_flag in [False, True]:
            try:
                simple_format = predict_simple_format(
                    tokenized_format.var_tokens,
                    to_1d_flag,
                )

                output_cands.append(
                    FormatPredictionResult.create_typed_format(
                        simple_format,
                        predict_types(
                            simple_format,
                            samples,
                        ),
                    )
                )
                break
            except (
                TypePredictionFailedError,
                SimpleFormatPredictionFailedError,
            ):
                pass

    if len(output_cands) > 1:
        raise MultiplePredictionResultsError(output_cands)

    if len(output_cands) == 0:
        raise NoPredictionResultError

    return output_cands[0]


def predict_format(
    content: ProblemContent,
) -> FormatPredictionResult:
    samples = content.get_samples()

    if len(samples) == 0:
        raise NoPredictionResultError

    try:
        multi_case = predict_multi_case_format(
            content
        )
    except NoMultiCaseFormatFoundError:
        # Preserve the established single-case path exactly when the
        # conservative repeated-case detector cannot prove its model.
        return _predict_single_case(content)
    except MultipleMultiCaseFormatsError as error:
        raise MultiplePredictionResultsError(
            error.candidates
        )

    return (
        FormatPredictionResult
        .create_repeated_case_typed_format(
            multi_case.prefix_format,
            multi_case.case_format,
            multi_case.case_count_var,
            multi_case.var_to_type,
        )
    )
