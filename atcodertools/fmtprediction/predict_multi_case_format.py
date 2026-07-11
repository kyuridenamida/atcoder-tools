import re
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.models.calculator import (
    EvaluateError,
)
from atcodertools.fmtprediction.models.format import Format
from atcodertools.fmtprediction.models.type import Type
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
    merge_type_dicts,
)
from atcodertools.fmtprediction.token_manager import (
    TokenManager,
)
from atcodertools.fmtprediction.tokenize_format import (
    NoFormatFoundError,
    search_formats_with_minimum_vars,
)


MAX_SAMPLE_CASE_COUNT = 100000

_SIMPLE_NAME_RE = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]*$"
)

_INDEXED_NAME_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9]*)_([A-Za-z0-9]+)$"
)


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


def _nonempty_lines(text: str) -> List[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _normalize_tex_atom(value: str) -> str:
    value = value.strip()

    command_pattern = re.compile(
        r"\\(?:text|rm|it|mathrm)\{([^{}]*)\}"
    )

    previous = None

    while previous != value:
        previous = value
        value = command_pattern.sub(
            r"\1",
            value,
        )

    value = value.replace("{", "")
    value = value.replace("}", "")
    value = value.replace("\\", "")
    value = value.replace(" ", "")

    return value


def _is_ellipsis_line(line: str) -> bool:
    normalized = _normalize_tex_atom(line).lower()

    return (
        normalized in ("vdots", "dots", "cdots", "...")
        or "..." in normalized
    )


def _simple_variable_name(
    text: str,
) -> Optional[str]:
    normalized = _normalize_tex_atom(text)

    if _SIMPLE_NAME_RE.fullmatch(normalized):
        return normalized

    return None


def _parse_indexed_variable(
    token: str,
) -> Optional[Tuple[str, str]]:
    normalized = _normalize_tex_atom(token)
    match = _INDEXED_NAME_RE.fullmatch(
        normalized
    )

    if match is None:
        return None

    return match.group(1), match.group(2)


def _extract_wrapper_prefix(
    text: str,
) -> Optional[str]:
    """
    Recognize a wrapper block such as:

        T
        test_1
        test_2
        ...
        test_T

    The actual per-case format must be supplied by a second block.
    """
    lines = _nonempty_lines(text)

    if len(lines) < 5:
        return None

    count_var = _simple_variable_name(
        lines[0]
    )

    if count_var is None:
        return None

    saw_ellipsis = False
    indices = []

    for line in lines[1:]:
        if _is_ellipsis_line(line):
            saw_ellipsis = True
            continue

        tokens = line.split()

        if len(tokens) != 1:
            return None

        parsed = _parse_indexed_variable(
            tokens[0]
        )

        if parsed is None:
            return None

        base, index = parsed

        if base.lower() not in (
            "test",
            "case",
        ):
            return None

        indices.append(index)

    if not saw_ellipsis:
        return None

    required_indices = {
        "1",
        "2",
        count_var,
    }

    if not required_indices.issubset(
        set(indices)
    ):
        return None

    return count_var + "\n"


def _parse_indexed_row(
    line: str,
) -> Optional[Tuple[List[str], str]]:
    tokens = line.split()

    if not tokens:
        return None

    bases = []
    row_index = None

    for token in tokens:
        parsed = _parse_indexed_variable(
            token
        )

        if parsed is None:
            return None

        base, index = parsed

        if row_index is None:
            row_index = index
        elif row_index != index:
            return None

        bases.append(base)

    return bases, row_index


def _extract_single_block_indexed_layout(
    text: str,
) -> Optional[Tuple[str, str]]:
    """
    Recognize a fixed-arity indexed layout such as:

        Q
        H_1 W_1 K_1
        H_2 W_2 K_2
        ...
        H_Q W_Q K_Q

    This deliberately does not match ordinary one-line arrays such as
    ``N`` followed by ``A_1 ... A_N``.
    """
    lines = _nonempty_lines(text)

    if len(lines) < 5:
        return None

    count_var = _simple_variable_name(
        lines[0]
    )

    if count_var is None:
        return None

    ellipsis_positions = [
        index
        for index, line in enumerate(lines[1:], 1)
        if _is_ellipsis_line(line)
    ]

    if len(ellipsis_positions) != 1:
        return None

    ellipsis_index = ellipsis_positions[0]

    rows_before = lines[1:ellipsis_index]
    rows_after = lines[ellipsis_index + 1:]

    if len(rows_before) < 2:
        return None

    if len(rows_after) != 1:
        return None

    first = _parse_indexed_row(
        rows_before[0]
    )
    second = _parse_indexed_row(
        rows_before[1]
    )
    final = _parse_indexed_row(
        rows_after[0]
    )

    if (
        first is None
        or second is None
        or final is None
    ):
        return None

    first_bases, first_index = first
    second_bases, second_index = second
    final_bases, final_index = final

    if first_bases != second_bases:
        return None

    if first_bases != final_bases:
        return None

    if first_index != "1":
        return None

    if second_index != "2":
        return None

    if final_index != count_var:
        return None

    prefix_text = count_var + "\n"
    case_text = " ".join(first_bases) + "\n"

    return prefix_text, case_text


def _predict_simple_format_candidates(
    input_format_text: str,
) -> List[Format]:
    try:
        tokenized_candidates = (
            search_formats_with_minimum_vars(
                input_format_text
            )
        )
    except NoFormatFoundError:
        return []

    result = []
    seen = set()

    for tokenized_candidate in tokenized_candidates:
        for to_1d_flag in (False, True):
            try:
                candidate = predict_simple_format(
                    tokenized_candidate.var_tokens,
                    to_1d_flag,
                )
            except SimpleFormatPredictionFailedError:
                continue

            signature = str(candidate)

            if signature not in seen:
                seen.add(signature)
                result.append(candidate)

            break

    return result


def _multi_case_evidence_context(
    content: ProblemContent,
) -> str:
    """
    Collect prose suitable for testcase-count evidence.

    The testcase declaration is often in the problem statement rather
    than in the input section. The original HTML is therefore included,
    but scripts, styles, and the hidden English statement are removed.
    """
    contexts = [
        content.get_input_format_context(),
    ]

    if content.original_html:
        soup = BeautifulSoup(
            content.original_html,
            "html.parser",
        )

        for element in soup.find_all(
            ["script", "style"],
        ):
            element.extract()

        for element in soup.find_all(
            "span",
            {"class": "lang-en"},
        ):
            element.extract()

        contexts.append(
            soup.get_text(
                " ",
                strip=True,
            )
        )

    return " ".join(
        " ".join(context.split())
        for context in contexts
        if context
    )


def _context_supports_count_variable(
    context: str,
    variable_name: str,
) -> bool:
    normalized = " ".join(
        context.split()
    )

    if not normalized:
        return False

    name_pattern = (
        r"(?<![A-Za-z0-9_])"
        + re.escape(variable_name)
        + r"(?![A-Za-z0-9_])"
    )

    patterns = (
        # Japanese: Q 個のテストケース / Q テストケース
        (
            name_pattern
            + r".{0,40}"
            + r"(?:個(?:\s*の)?\s*)?テストケース"
        ),
        # English: Q test cases / Q cases
        (
            name_pattern
            + r".{0,40}"
            + r"(?:test\s+cases?|cases?)"
        ),
        # Japanese inverse order: テストケースの数は Q
        (
            r"テストケース(?:の)?数"
            + r".{0,40}"
            + name_pattern
        ),
        # English inverse order: the number of test cases is Q
        (
            r"(?:number\s+of\s+(?:the\s+)?test\s+cases|"
            r"test\s+case\s+count)"
            + r".{0,40}"
            + name_pattern
        ),
    )

    return any(
        re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )
        is not None
        for pattern in patterns
    )


def _candidate_layouts(
    content: ProblemContent,
):
    blocks = content.get_input_format_blocks()

    if len(blocks) == 2:
        # Original split representation:
        # prefix block + case block.
        yield (
            "split",
            blocks[0],
            blocks[1],
            False,
        )

        wrapper_prefix = (
            _extract_wrapper_prefix(
                blocks[0]
            )
        )

        if wrapper_prefix is not None:
            yield (
                "wrapper",
                wrapper_prefix,
                blocks[1],
                True,
            )

    if len(blocks) == 1:
        indexed = (
            _extract_single_block_indexed_layout(
                blocks[0]
            )
        )

        if indexed is not None:
            prefix_text, case_text = indexed

            # An indexed row sequence is structurally indistinguishable
            # from ordinary parallel arrays such as
            #
            #   n
            #   p_1 l_1
            #   p_2 l_2
            #   ...
            #   p_n l_n
            #
            # Therefore structural evidence alone is insufficient here.
            # The input-section prose must also explicitly identify the
            # count variable as a testcase count.
            yield (
                "single_block_indexed",
                prefix_text,
                case_text,
                False,
            )


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


def predict_multi_case_format(
    content: ProblemContent,
) -> MultiCaseFormatPrediction:
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
        prefix_candidates = (
            _predict_simple_format_candidates(
                prefix_text
            )
        )
        case_candidates = (
            _predict_simple_format_candidates(
                case_text
            )
        )

        for prefix_format in prefix_candidates:
            prefix_names = (
                _format_variable_names(
                    prefix_format
                )
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
                    case_names = (
                        _format_variable_names(
                            case_format
                        )
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
