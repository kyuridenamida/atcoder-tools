import re
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
    candidate_layouts,
    context_supports_count_variable,
    multi_case_evidence_context,
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

from atcodertools.fmtprediction.tokenize_format import (
    collapse_string_runs,
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


_LAYOUT_HSPACE_PATTERN = re.compile(
    r"\\hspace\*?\s*\{[^{}]*\}"
)

_BRACED_LAYOUT_STYLE_PATTERN = re.compile(
    r"""
    \\
    (?:
        text
        |mathrm
        |rm
        |it
    )
    \s*
    \{
        (?P<body>[^{}]*)
    \}
    """,
    re.VERBOSE,
)

_RESERVED_PLACEHOLDER_PATTERN = re.compile(
    r"^(?:query|operation|op|case|test|testcase)$",
    re.IGNORECASE,
)

_BRACED_SPACED_INDEX_PATTERN = re.compile(
    r"""
    (?P<base>\b[A-Za-z][A-Za-z0-9]*)
    \s*
    _
    \s*
    \{
        \s*
        (?P<index>[^{}\n]+?)
        \s*
    \}
    """,
    re.VERBOSE,
)

_UNBRACED_SPACED_INDEX_PATTERN = re.compile(
    r"""
    (?P<base>\b[A-Za-z][A-Za-z0-9]*)
    \s*
    _
    \s*
    (?P<index>[A-Za-z0-9]+)
    """,
    re.VERBOSE,
)


def _remove_layout_hspace_commands(
    input_format_text: str,
) -> str:
    """Remove TeX horizontal spacing commands."""
    return _LAYOUT_HSPACE_PATTERN.sub(
        "",
        input_format_text,
    )


def _unwrap_layout_style_commands(
    input_format_text: str,
) -> str:
    """
    Remove presentation-only TeX wrappers.

    Query, operation and test-case placeholders are
    intentionally preserved for their dedicated
    recognizers.
    """

    def replace(match):
        body = match.group("body").strip()

        if _RESERVED_PLACEHOLDER_PATTERN.fullmatch(
            body
        ):
            return match.group(0)

        return body

    current = input_format_text

    for _ in range(8):
        updated = _BRACED_LAYOUT_STYLE_PATTERN.sub(
            replace,
            current,
        )

        if updated == current:
            break

        current = updated

    return current


def _normalize_spaced_variable_indices(
    input_format_text: str,
) -> str:
    """
    Normalize spaces only inside variable index atoms.

    Ordinary separators such as ``N M`` are preserved.
    """
    current = input_format_text

    for _ in range(8):
        updated = _BRACED_SPACED_INDEX_PATTERN.sub(
            lambda match: "{}_{{{}}}".format(
                match.group("base"),
                re.sub(
                    r"\s+",
                    "",
                    match.group("index"),
                ),
            ),
            current,
        )

        updated = _UNBRACED_SPACED_INDEX_PATTERN.sub(
            lambda match: "{}_{}".format(
                match.group("base"),
                match.group("index"),
            ),
            updated,
        )

        if updated == current:
            break

        current = updated

    return current


_FIXED_INDEX_SCALAR_PATTERN = re.compile(
    r"(?P<base>[A-Za-z][A-Za-z0-9_]*)_"
    r"(?:\{(?P<braced>[0-9]+)\}|"
    r"(?P<plain>[0-9]+))"
)

_FIXED_PREFIX_REFERENCE_PATTERN = re.compile(
    r"(?P<base>[A-Za-z][A-Za-z0-9_]*)_"
    r"\{\s*(?P<fixed>[0-9]+)\s*,\s*"
    r"(?P<varying>[^{}\n]+?)\s*\}"
)

_INDEX_BODY_PATTERN = re.compile(
    r"_\{(?P<body>[^{}\n]+)\}"
)

_IDENTIFIER_WORD_PATTERN = re.compile(
    r"[A-Za-z][A-Za-z0-9_]*"
)

_DIGIT_WORDS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


def _fixed_index_alias(
    base,
    literal,
):
    suffix = "".join(
        _DIGIT_WORDS[digit]
        for digit in literal
    )

    return "{}fixed{}".format(
        base,
        suffix,
    )


def _fixed_index_atom_pattern(
    base,
    literal,
):
    return re.compile(
        r"(?<![A-Za-z0-9_])"
        + re.escape(base)
        + r"_(?:\{"
        + re.escape(literal)
        + r"\}|"
        + re.escape(literal)
        + r")(?![A-Za-z0-9_])"
    )


def _declared_fixed_index_scalars(
    input_format_text,
):
    declarations = set()

    for line in input_format_text.splitlines():
        tokens = [
            token.rstrip(",")
            for token in line.split()
        ]

        if not tokens:
            continue

        matches = [
            _FIXED_INDEX_SCALAR_PATTERN.fullmatch(
                token
            )
            for token in tokens
        ]

        if any(
            match is None
            for match in matches
        ):
            continue

        for match in matches:
            declarations.add(
                (
                    match.group("base"),
                    (
                        match.group("braced")
                        or match.group("plain")
                    ),
                )
            )

    return declarations


def _contains_identifier(
    expression,
    identifier,
):
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])"
        + re.escape(identifier)
        + r"(?![A-Za-z0-9_])"
    )

    return (
        pattern.search(expression)
        is not None
    )


def _normalize_indexed_identifier_aliases(
    input_format_text,
):
    """
    Build a recognition-only view for independent fixed-index segments.

    A source such as ``N_1`` and ``u_{1,j}`` is normalized only when:

    - the fixed-index scalar is declared as an input field,
    - that scalar is later used as an index bound,
    - the same sequence base has at least two literal first coordinates,
    - each literal coordinate is tied to a matching fixed-index scalar,
    - all generated aliases are collision-free.

    Ordinary arrays and dense multidimensional grids remain unchanged.
    """
    index_bodies = [
        match.group("body")
        for match in _INDEX_BODY_PATTERN.finditer(
            input_format_text
        )
    ]

    reserved_names = set(
        _IDENTIFIER_WORD_PATTERN.findall(
            input_format_text
        )
    )

    scalar_aliases = {}

    for base, literal in sorted(
        _declared_fixed_index_scalars(
            input_format_text
        )
    ):
        atom_pattern = (
            _fixed_index_atom_pattern(
                base,
                literal,
            )
        )

        if not any(
            atom_pattern.search(body)
            is not None
            for body in index_bodies
        ):
            continue

        alias = _fixed_index_alias(
            base,
            literal,
        )

        if alias in reserved_names:
            continue

        scalar_aliases[
            (base, literal)
        ] = alias

        reserved_names.add(alias)

    if not scalar_aliases:
        return input_format_text

    temporary = input_format_text

    for (
        base,
        literal,
    ), alias in scalar_aliases.items():
        temporary = (
            _fixed_index_atom_pattern(
                base,
                literal,
            ).sub(
                alias,
                temporary,
            )
        )

    aliases_by_literal = {}

    for (
        _,
        literal,
    ), alias in scalar_aliases.items():
        aliases_by_literal.setdefault(
            literal,
            set(),
        ).add(alias)

    references_by_base = {}

    for match in (
        _FIXED_PREFIX_REFERENCE_PATTERN
        .finditer(temporary)
    ):
        references_by_base.setdefault(
            match.group("base"),
            [],
        ).append(
            (
                match.group("fixed"),
                match.group("varying").strip(),
            )
        )

    sequence_aliases = {}
    used_scalar_aliases = set()

    for base, references in (
        references_by_base.items()
    ):
        all_base_occurrences = re.findall(
            (
                r"(?<![A-Za-z0-9_])"
                + re.escape(base)
                + r"_"
            ),
            temporary,
        )

        if (
            len(all_base_occurrences)
            != len(references)
        ):
            continue

        fixed_values = {
            fixed
            for fixed, _
            in references
        }

        if len(fixed_values) < 2:
            continue

        base_aliases = {}
        base_used_scalars = set()
        valid = True

        for fixed in fixed_values:
            scalar_candidates = (
                aliases_by_literal.get(
                    fixed,
                    set(),
                )
            )

            matching_scalars = {
                alias
                for current_fixed, varying
                in references
                if current_fixed == fixed
                for alias in scalar_candidates
                if _contains_identifier(
                    varying,
                    alias,
                )
            }

            if not matching_scalars:
                valid = False
                break

            alias = _fixed_index_alias(
                base,
                fixed,
            )

            if alias in reserved_names:
                valid = False
                break

            base_aliases[
                (base, fixed)
            ] = alias

            base_used_scalars.update(
                matching_scalars
            )

        if not valid:
            continue

        sequence_aliases.update(
            base_aliases
        )

        used_scalar_aliases.update(
            base_used_scalars
        )

        reserved_names.update(
            base_aliases.values()
        )

    if not sequence_aliases:
        return input_format_text

    normalized = input_format_text

    for (
        base,
        literal,
    ), alias in scalar_aliases.items():
        if alias not in used_scalar_aliases:
            continue

        normalized = (
            _fixed_index_atom_pattern(
                base,
                literal,
            ).sub(
                alias,
                normalized,
            )
        )

    def replace_reference(match):
        key = (
            match.group("base"),
            match.group("fixed"),
        )

        alias = sequence_aliases.get(key)

        if alias is None:
            return match.group(0)

        return "{}_{{{}}}".format(
            alias,
            match.group("varying").strip(),
        )

    return (
        _FIXED_PREFIX_REFERENCE_PATTERN.sub(
            replace_reference,
            normalized,
        )
    )


def _remove_inline_math_delimiters(
    input_format_text,
):
    """
    Remove TeX inline-math wrappers from a recognition-only view.
    """
    if input_format_text is None:
        return None

    return (
        str(input_format_text)
        .replace(r"\(", "")
        .replace(r"\)", "")
    )


class _InlineMathDelimiterContentView:
    """
    Non-mutating recognition view of ProblemContent.
    """

    def __init__(self, content):
        self._content = content

    def get_input_format(self):
        return _remove_inline_math_delimiters(
            self._content.get_input_format()
        )

    def get_input_format_text(self):
        return self.get_input_format()

    @property
    def input_format_text(self):
        return self.get_input_format()

    def get_input_format_blocks(self):
        blocks = (
            self._content
            .get_input_format_blocks()
            or []
        )

        return [
            _remove_inline_math_delimiters(
                block
            )
            for block in blocks
        ]

    @property
    def input_format_blocks(self):
        return self.get_input_format_blocks()

    def get_input_format_context(self):
        getter = getattr(
            self._content,
            "get_input_format_context",
            None,
        )

        if getter is None:
            return self.get_input_format()

        context = getter()

        if context is None:
            return self.get_input_format()

        return _remove_inline_math_delimiters(
            context
        )

    @property
    def input_format_context_text(self):
        return self.get_input_format_context()

    def __getattr__(self, name):
        return getattr(
            self._content,
            name,
        )


def _inline_math_delimiter_content_view(
    content,
):
    """
    Normalize all input-format representations without mutation.
    """
    if isinstance(
        content,
        _InlineMathDelimiterContentView,
    ):
        return content

    input_format = content.get_input_format()
    blocks = (
        content.get_input_format_blocks()
        or []
    )

    has_delimiter = (
        (
            input_format is not None
            and (
                r"\(" in str(input_format)
                or r"\)" in str(input_format)
            )
        )
        or any(
            r"\(" in str(block)
            or r"\)" in str(block)
            for block in blocks
        )
    )

    if not has_delimiter:
        return content

    return _InlineMathDelimiterContentView(
        content
    )


def _normalize_layout_tex_commands(
    input_format_text: str,
) -> str:
    """
    Build a recognition-only view without mutating raw text.
    """
    input_format_text = _remove_inline_math_delimiters(
        input_format_text
    )
    normalized = _remove_layout_hspace_commands(
        input_format_text
    )
    normalized = _unwrap_layout_style_commands(
        normalized
    )
    normalized = _normalize_spaced_variable_indices(
        normalized
    )
    normalized = (
        _normalize_indexed_identifier_aliases(
            normalized
        )
    )
    return normalized


def _predict_simple_format_candidate_groups_without_string_collapse(
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
                _normalize_layout_tex_commands(
                    input_format_text
                )
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


def _predict_simple_format_candidate_groups(
    input_format_text: str,
):
    candidate_groups = list(
        _predict_simple_format_candidate_groups_without_string_collapse(
            input_format_text
        )
    )

    if candidate_groups:
        return candidate_groups

    collapsed_input_format = collapse_string_runs(
        input_format_text
    )

    if collapsed_input_format == input_format_text:
        return []

    return list(
        _predict_simple_format_candidate_groups_without_string_collapse(
            collapsed_input_format
        )
    )


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


def _normalized_wrapper_placeholder_name(
    variable_name,
):
    normalized = variable_name.lower()

    prefixes = (
        "mathrm",
        "text",
        "rm",
        "it",
    )

    changed = True

    while changed:
        changed = False

        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[
                    len(prefix):
                ]
                changed = True
                break

    return normalized


def _is_wrapper_placeholder_split_candidate(
    candidate,
    wrapper,
):
    if candidate.layout != "split":
        return False

    if wrapper.layout != "wrapper":
        return False

    if (
        candidate.case_count_var
        != wrapper.case_count_var
    ):
        return False

    if (
        str(candidate.case_format)
        != str(wrapper.case_format)
    ):
        return False

    wrapper_names = (
        _format_variable_names(
            wrapper.prefix_format
        )
    )

    candidate_variables = (
        candidate.prefix_format.all_vars()
    )

    candidate_names = {
        variable.name
        for variable in candidate_variables
    }

    if not wrapper_names.issubset(
        candidate_names
    ):
        return False

    if candidate_names == wrapper_names:
        return False

    extra_variables = [
        variable
        for variable in candidate_variables
        if variable.name
        not in wrapper_names
    ]

    if not extra_variables:
        return False

    prefix_text = str(
        candidate.prefix_format
    )

    for variable in extra_variables:
        if variable.dim_num() != 1:
            return False

        placeholder_name = (
            _normalized_wrapper_placeholder_name(
                variable.name
            )
        )

        if placeholder_name not in {
            "case",
            "test",
        }:
            return False

        expected_pattern = (
            "(Parallel: {} | 1 to {})"
            .format(
                variable.name,
                candidate.case_count_var,
            )
        )

        if expected_pattern not in prefix_text:
            return False

    return True


def _prefer_explicit_wrapper_candidates(
    candidates,
):
    wrapper_candidates = [
        candidate
        for candidate in candidates
        if candidate.layout == "wrapper"
    ]

    if not wrapper_candidates:
        return candidates

    return [
        candidate
        for candidate in candidates
        if not any(
            _is_wrapper_placeholder_split_candidate(
                candidate,
                wrapper,
            )
            for wrapper in wrapper_candidates
        )
    ]


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


def _collect_single_case_candidates(
    input_format: str,
    samples,
):
    output_candidates = []

    for candidate_group in (
        _predict_simple_format_candidate_groups_without_string_collapse(
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

            break

    return output_candidates


def _deduplicate_candidates(
    candidates,
):
    deduplicated = []
    seen = set()

    for candidate in candidates:
        signature = str(
            candidate.format
        )

        if signature in seen:
            continue

        seen.add(signature)
        deduplicated.append(
            candidate
        )

    return deduplicated


def _candidate_string_dimensions(
    candidate,
):
    dimensions = {}

    for variable in (
        candidate.format.all_vars()
    ):
        if str(variable.type) != "Type.str":
            continue

        dimensions[variable.name] = (
            variable.dim_num()
        )

    return dimensions


def _contains_two_index_variable(
    input_format,
    variable_name,
):
    escaped_name = re.escape(
        variable_name
    )

    pattern = (
        escaped_name
        + r"_\{[^{}\n]*,[^{}\n]*\}"
    )

    return (
        re.search(
            pattern,
            input_format,
        )
        is not None
    )


def _contains_one_index_variable(
    input_format,
    variable_name,
):
    escaped_name = re.escape(
        variable_name
    )

    pattern = (
        escaped_name
        + r"_\{[^{},\n]+\}"
    )

    return (
        re.search(
            pattern,
            input_format,
        )
        is not None
    )


def _samples_are_single_token_rows(
    samples,
):
    found_body = False

    for sample in samples:
        lines = (
            sample.get_input()
            .splitlines()
        )

        if len(lines) < 2:
            return False

        body_lines = [
            line
            for line in lines[1:]
            if line != ""
        ]

        if not body_lines:
            return False

        if any(
            len(line.split()) != 1
            for line in body_lines
        ):
            return False

        found_body = True

    return found_body


def _is_structural_string_grid_collapse(
    original_candidate,
    collapsed_candidate,
    input_format,
    collapsed_input_format,
    samples,
):
    if not _samples_are_single_token_rows(
        samples
    ):
        return False

    original_dimensions = (
        _candidate_string_dimensions(
            original_candidate
        )
    )
    collapsed_dimensions = (
        _candidate_string_dimensions(
            collapsed_candidate
        )
    )

    shared_names = (
        set(original_dimensions)
        & set(collapsed_dimensions)
    )

    matching_names = []

    for name in shared_names:
        if (
            collapsed_dimensions[name] != 1
        ):
            continue

        if (
            original_dimensions[name]
            not in (1, 2)
        ):
            continue

        if not _contains_two_index_variable(
            input_format,
            name,
        ):
            continue

        if not _contains_one_index_variable(
            collapsed_input_format,
            name,
        ):
            continue

        matching_names.append(name)

    return len(matching_names) == 1


def _collapse_spaced_grid_row(
    line,
):
    tokens = line.split()

    if len(tokens) < 3:
        return line

    references = []

    for token in tokens:
        match = re.fullmatch(
            (
                r"(?P<name>"
                r"[A-Za-z][A-Za-z0-9_]*"
                r")_\{\s*"
                r"(?P<outer>[^,{}]+?)"
                r"\s*,\s*"
                r"(?P<inner>[^{}]+?)"
                r"\s*\}"
            ),
            token,
        )

        if match is None:
            return line

        references.append(
            (
                match.group("name"),
                match.group("outer"),
                match.group("inner"),
            )
        )

    names = {
        name
        for name, _, _
        in references
    }

    outer_indices = {
        outer
        for _, outer, _
        in references
    }

    inner_indices = {
        inner
        for _, _, inner
        in references
    }

    if (
        len(names) != 1
        or len(outer_indices) != 1
        or len(inner_indices) < 2
    ):
        return line

    name = references[0][0]
    outer = references[0][1]

    return "{}_{{{}}}".format(
        name,
        outer,
    )


def _collapse_spaced_grid_rows(
    input_format,
):
    return "\n".join(
        _collapse_spaced_grid_row(
            line
        )
        for line in input_format.split(
            "\n"
        )
    )


def _collapse_compact_digit_grid_row(
    line,
):
    references = list(
        re.finditer(
            (
                r"(?P<name>"
                r"[A-Za-z][A-Za-z0-9_]*"
                r")_\{"
                r"(?P<combined>"
                r"[A-Za-z0-9+\-]+"
                r")\}"
            ),
            line,
        )
    )

    if len(references) < 3:
        return line

    names = {
        match.group("name")
        for match in references
    }

    if len(names) != 1:
        return line

    combined_indices = [
        match.group("combined")
        for match in references
    ]

    if any(
        len(index) < 2
        for index in combined_indices
    ):
        return line

    outer_indices = {
        index[:-1]
        for index in combined_indices
    }

    inner_indices = {
        index[-1]
        for index in combined_indices
    }

    if (
        len(outer_indices) != 1
        or len(inner_indices) < 2
    ):
        return line

    reference_span = line[
        references[0].start():
        references[-1].end()
    ]

    if any(
        character.isspace()
        for character in reference_span
    ):
        return line

    if not (
        "..." in reference_span
        or "…" in reference_span
        or "‥" in reference_span
    ):
        return line

    name = references[0].group(
        "name"
    )
    outer = next(
        iter(outer_indices)
    )

    return "{}_{{{}}}".format(
        name,
        outer,
    )


def _collapse_compact_digit_grid_rows(
    input_format,
):
    return "\n".join(
        _collapse_compact_digit_grid_row(
            line
        )
        for line in input_format.split(
            "\n"
        )
    )


def _predict_single_case(
    content: ProblemContent,
) -> FormatPredictionResult:
    input_format = content.get_input_format()
    samples = content.get_samples()

    original_candidates = (
        _deduplicate_candidates(
            _collect_single_case_candidates(
                input_format,
                samples,
            )
        )
    )

    collapsed_input_format = (
        collapse_string_runs(
            input_format
        )
    )

    collapsed_candidates = []

    if collapsed_input_format != input_format:
        collapsed_candidates = (
            _deduplicate_candidates(
                _collect_single_case_candidates(
                    collapsed_input_format,
                    samples,
                )
            )
        )

    spaced_grid_candidates = []

    if (
        not original_candidates
        and not collapsed_candidates
    ):
        spaced_grid_input_format = (
            _collapse_spaced_grid_rows(
                input_format
            )
        )

        if spaced_grid_input_format != input_format:
            spaced_grid_candidates = (
                _deduplicate_candidates(
                    _collect_single_case_candidates(
                        spaced_grid_input_format,
                        samples,
                    )
                )
            )

    compact_digit_grid_candidates = []

    if (
        not original_candidates
        and not collapsed_candidates
        and not spaced_grid_candidates
    ):
        compact_digit_grid_input_format = (
            _collapse_compact_digit_grid_rows(
                input_format
            )
        )

        if (
            compact_digit_grid_input_format
            != input_format
        ):
            compact_digit_grid_candidates = (
                _deduplicate_candidates(
                    _collect_single_case_candidates(
                        compact_digit_grid_input_format,
                        samples,
                    )
                )
            )

    if (
        len(original_candidates) == 1
        and len(collapsed_candidates) == 1
        and _is_structural_string_grid_collapse(
            original_candidates[0],
            collapsed_candidates[0],
            input_format,
            collapsed_input_format,
            samples,
        )
    ):
        output_candidates = collapsed_candidates

    elif original_candidates:
        output_candidates = original_candidates

    elif collapsed_candidates:
        output_candidates = collapsed_candidates

    elif spaced_grid_candidates:
        output_candidates = spaced_grid_candidates

    else:
        output_candidates = (
            compact_digit_grid_candidates
        )

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
        multi_case_evidence_context(
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
    ) in candidate_layouts(content):
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
                    and not context_supports_count_variable(
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

    valid_predictions = (
        _prefer_explicit_wrapper_candidates(
            valid_predictions
        )
    )

    if not valid_predictions:
        raise NoMultiCaseFormatFoundError

    if len(valid_predictions) > 1:
        raise MultipleMultiCaseFormatsError(
            valid_predictions
        )

    return valid_predictions[0]


def _predict_same_line_ragged_format(
    content: ProblemContent,
) -> FormatPredictionResult:
    from atcodertools.fmtprediction import (
        ragged_row,
        two_line_ragged_row,
    )

    try:
        prediction = (
            ragged_row
            .predict_same_line_ragged_rows(
                content
            )
        )
    except (
        ragged_row
        .NoRaggedRowPredictionError,
        ragged_row
        .MultipleRaggedRowPredictionsError,
    ):
        try:
            prediction = (
                two_line_ragged_row
                .predict_two_line_ragged_rows(
                    content
                )
            )
        except (
            two_line_ragged_row
            .NoTwoLineRaggedRowPredictionError,
            two_line_ragged_row
            .MultipleTwoLineRaggedRowPredictionsError,
        ):
            raise NoPredictionResultError from None

    return (
        FormatPredictionResult
        .create_ragged_row_typed_format(
            prediction.prefix_format,
            prediction.schema,
            prediction.var_to_type,
            prediction.suffix_format,
        )
    )


def predict_format(
    content: ProblemContent,
) -> FormatPredictionResult:
    content = _inline_math_delimiter_content_view(
        content
    )
    samples = content.get_samples()

    if not samples:
        raise NoPredictionResultError

    try:
        multi_case = predict_multi_case_format(
            content
        )
    except NoMultiCaseFormatFoundError:
        try:
            return _predict_single_case(
                content
            )
        except NoPredictionResultError:
            return (
                _predict_same_line_ragged_format(
                    content
                )
            )
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
