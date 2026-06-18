from atcodertools.client.atcoder import ProblemContent
from atcodertools.fmtprediction.predict_simple_format import predict_simple_format, SimpleFormatPredictionFailedError
from atcodertools.fmtprediction.tokenize_format import NoFormatFoundError, \
    search_formats_with_minimum_vars, collapse_string_runs
from atcodertools.fmtprediction.predict_types import predict_types, TypePredictionFailedError
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult


class NoPredictionResultError(Exception):
    pass


class MultiplePredictionResultsError(Exception):

    def __init__(self, cands):
        self.cands = cands


def _result_signature(result: FormatPredictionResult):
    """A structural signature used to deduplicate equivalent prediction
    results produced from different format-text variants."""
    return (str(result.format),
            tuple((var.name, var.type) for var in result.format.all_vars()))


def _collect_candidates(input_format: str, samples) -> list:
    try:
        tokenized_possible_formats = search_formats_with_minimum_vars(
            input_format)
    except NoFormatFoundError:
        return []

    output_cands = []
    for format in tokenized_possible_formats:
        for to_1d_flag in [False, True]:
            try:
                simple_format = predict_simple_format(
                    format.var_tokens, to_1d_flag)
                output_cands.append(
                    FormatPredictionResult.create_typed_format(simple_format, predict_types(simple_format, samples)))
                break
            except (TypePredictionFailedError, SimpleFormatPredictionFailedError):
                pass
    return output_cands


def predict_format(content: ProblemContent) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()

    if len(samples) == 0:
        raise NoPredictionResultError

    # Try the format text as-is first.
    output_cands = _collect_candidates(input_format, samples)

    # If that doesn't produce any candidate, retry with a variant where glued /
    # dotted runs of a single variable are collapsed into a string (character
    # grids, single strings, ...). This is only used as a fallback so that
    # already-resolvable formats keep their original (unique) interpretation.
    if len(output_cands) == 0:
        collapsed = collapse_string_runs(input_format)
        if collapsed != input_format:
            seen_signatures = set()
            for cand in _collect_candidates(collapsed, samples):
                signature = _result_signature(cand)
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)
                output_cands.append(cand)

    if len(output_cands) > 1:
        raise MultiplePredictionResultsError(output_cands)
    if len(output_cands) == 0:
        raise NoPredictionResultError
    return output_cands[0]
