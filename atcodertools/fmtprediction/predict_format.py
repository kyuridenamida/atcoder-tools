from typing import Dict, List

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.models.calculator import (
    EvaluateError,
)
from atcodertools.fmtprediction.models.format import Format
from atcodertools.fmtprediction.models.format_prediction_result import (
    FormatPredictionResult,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.multi_case_layout import (
    _candidate_layouts,
    _context_supports_count_variable,
    _multi_case_evidence_context,
)
from atcodertools.fmtprediction.predict_simple_format import (
    SimpleFormatPredictionFailedError,
    predict_simple_format,
)
from atcodertools.fmtprediction.predict_types import (
    InvalidLoopIndexError,
    InvalidLoopSizeError,
    TooLessFetchesError,
    TooManyFetchesError,
    TypePredictor,
    TypePredictionFailedError,
    merge_type_dicts,
    predict_types,
)
from atcodertools.fmtprediction.token_manager import TokenManager
from atcodertools.fmtprediction.tokenize_format import (
    NoFormatFoundError,
    search_formats_with_minimum_vars,
)


MAX_SAMPLE_CASE_COUNT = 100000


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):
    def __init__(self, cands):
        self.cands = cands


class NoMultiCaseFormatFoundError(Exception):
    pass


class MultipleMultiCaseFormatsError(Exception):
    def __init__(self, candidates):
        self.candidates = candidates


class MultiCaseFormatPrediction:
    def __init__(
        self,
        prefix_format: Format,
        case_format: Format,
        case_count_var: str,
        var_to_type: Dict[str, Type],
        layout: str,
    ):
        self.prefix_format = prefix_format
        self.case_format = case_format
        self.case_count_var = case_count_var
        self.var_to_type = var_to_type
        self.layout = layout


def _predict_simple_format_candidate_groups(
    input_format_text: str,
) -> List[List[Format]]:
    """
    Return simple-format variants grouped by tokenized candidate.

    A group retains both the ordinary interpretation and the optional
    one-dimensional fallback. The caller decides which successfully
    validated variant to accept.
    """
    try:
        tokenized_candidates = (
            search_formats_with_minimum_vars(
                input_format_text
            )
        )
    except NoFormatFoundError:
        return []

    groups = []

    for tokenized_candidate in tokenized_candidates:
        group = []
        seen = set()

        for to_1d_flag in (False, True):
            try:
                candidate = predict_simple_format(
                    tokenized_candidate.var_tokens,
                    to_1d_flag,
                )
            except SimpleFormatPredictionFailedError:
                continue

            signature = str(candidate)

            if signature in seen:
                continue

            seen.add(signature)
            group.append(candidate)

        if group:
            groups.append(group)

    return groups


def _predict_simple_format_candidates(
    input_format_text: str,
) -> List[Format]:
    """
    Flatten all simple-format variants for repeated-case pairing.
    """
    return _unique_formats(
        [
            candidate
            for group in (
                _predict_simple_format_candidate_groups(
                    input_format_text
                )
            )
            for candidate in group
        ]
    )


def _unique_formats(formats: List[Format]) -> List[Format]:
    result = []
    seen = set()

    for format_ in formats:
        signature = str(format_)

        if signature in seen:
            continue

        seen.add(signature)
        result.append(format_)

    return result


def _scalar_variable_names(
    format_: Format,
) -> List[str]:
    return [
        variable.name
        for variable in format_.all_vars()
        if variable.dim_num() == 0
    ]


def _format_variable_names(format_: Format):
    return {
        variable.name
        for variable in format_.all_vars()
    }


def _validate_candidate_on_samples(
    prefix_format: Format,
    case_format: Format,
    case_count_var: str,
    samples,
):
    """
    Validate a repeated-case candidate by consuming every sample token.

    The same TypePredictor used by ordinary prediction consumes the
    prefix and each case. A candidate is accepted only when the declared
    case count is a reasonable positive integer and all tokens are used.
    """
    merged_types = {}

    for sample in samples:
        token_manager = TokenManager(
            sample.get_input().split()
        )
        prefix_predictor = TypePredictor(
            prefix_format
        )
        prefix_predictor.consume(
            token_manager
        )

        case_count = (
            prefix_predictor.get_actual_value(
                case_count_var
            )
        )

        if type(case_count) is not int:
            raise InvalidLoopSizeError

        if (
            case_count <= 0
            or case_count > MAX_SAMPLE_CASE_COUNT
        ):
            raise InvalidLoopSizeError

        merged_types = merge_type_dicts(
            merged_types,
            prefix_predictor.get_typing_result(),
        )

        for _ in range(case_count):
            case_predictor = TypePredictor(
                case_format
            )
            case_predictor.consume(
                token_manager
            )
            merged_types = merge_type_dicts(
                merged_types,
                case_predictor.get_typing_result(),
            )

        if not token_manager.is_terminal():
            raise TooManyFetchesError

    return merged_types


def _predict_single_case(
    content: ProblemContent,
) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()
    output_candidates = []

    for candidate_group in (
        _predict_simple_format_candidate_groups(
            input_format
        )
    ):
        for simple_format in candidate_group:
            try:
                var_to_type = predict_types(
                    simple_format,
                    samples,
                )
            except TypePredictionFailedError:
                continue

            output_candidates.append(
                FormatPredictionResult.create_typed_format(
                    simple_format,
                    var_to_type,
                )
            )

            # Preserve the historical behavior: once one variant of a
            # tokenized candidate passes type prediction, do not try its
            # one-dimensional fallback.
            break

    if len(output_candidates) > 1:
        raise MultiplePredictionResultsError(
            output_candidates
        )

    if not output_candidates:
        raise NoPredictionResultError

    return output_candidates[0]


def predict_multi_case_format(
    content: ProblemContent,
) -> MultiCaseFormatPrediction:
    """
    Predict a repeated-case format.

    Layout recognition is delegated to multi_case_layout, while candidate
    construction and sample validation live in this orchestration module.
    """
    samples = content.get_samples()

    if not samples:
        raise NoMultiCaseFormatFoundError

    evidence_context = (
        _multi_case_evidence_context(
            content
        )
    )
    valid_predictions = []
    seen = set()

    for (
        layout,
        prefix_text,
        case_text,
        structural_evidence,
    ) in _candidate_layouts(content):
        prefix_candidates = _unique_formats(
            _predict_simple_format_candidates(
                prefix_text
            )
        )
        case_candidates = _unique_formats(
            _predict_simple_format_candidates(
                case_text
            )
        )

        for prefix_format in prefix_candidates:
            prefix_names = _format_variable_names(
                prefix_format
            )

            for case_count_var in (
                _scalar_variable_names(
                    prefix_format
                )
            ):
                if (
                    not structural_evidence
                    and not _context_supports_count_variable(
                        evidence_context,
                        case_count_var,
                    )
                ):
                    continue

                for case_format in case_candidates:
                    case_names = _format_variable_names(
                        case_format
                    )

                    if prefix_names.intersection(
                        case_names
                    ):
                        continue

                    try:
                        var_to_type = (
                            _validate_candidate_on_samples(
                                prefix_format,
                                case_format,
                                case_count_var,
                                samples,
                            )
                        )
                    except (
                        AssertionError,
                        EvaluateError,
                        InvalidLoopIndexError,
                        InvalidLoopSizeError,
                        KeyError,
                        NotImplementedError,
                        StopIteration,
                        TooLessFetchesError,
                        TooManyFetchesError,
                        ValueError,
                    ):
                        continue

                    signature = (
                        str(prefix_format),
                        str(case_format),
                        case_count_var,
                    )

                    if signature in seen:
                        continue

                    seen.add(signature)
                    valid_predictions.append(
                        MultiCaseFormatPrediction(
                            prefix_format,
                            case_format,
                            case_count_var,
                            var_to_type,
                            layout,
                        )
                    )

    if not valid_predictions:
        raise NoMultiCaseFormatFoundError

    if len(valid_predictions) > 1:
        raise MultipleMultiCaseFormatsError(
            valid_predictions
        )

    return valid_predictions[0]


def predict_format(
    content: ProblemContent,
) -> FormatPredictionResult:
    samples = content.get_samples()

    if not samples:
        raise NoPredictionResultError

    try:
        multi_case = predict_multi_case_format(
            content
        )
    except NoMultiCaseFormatFoundError:
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
