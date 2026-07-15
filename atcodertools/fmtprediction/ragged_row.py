from dataclasses import dataclass
import re
from typing import Dict, List, Tuple

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.models.format import (
    Format,
)
from atcodertools.fmtprediction.models.input_specification import (
    InputSpecification,
    InputTokenKind,
)
from atcodertools.fmtprediction.models.type import (
    Type,
)
from atcodertools.fmtprediction.predict_simple_format import (
    SimpleFormatPredictionFailedError,
    predict_simple_format,
)
from atcodertools.fmtprediction.predict_types import (
    EvaluateError,
    InvalidLoopIndexError,
    InvalidLoopSizeError,
    TooLessFetchesError,
    TooManyFetchesError,
    TypePredictor,
    is_float,
    is_int,
    merge_type_dicts,
)
from atcodertools.fmtprediction.token_manager import (
    TokenManager,
)
from atcodertools.fmtprediction.tokenize_format import (
    NoFormatFoundError,
    search_formats_with_minimum_vars,
)


class NoRaggedRowPredictionError(Exception):
    pass


class MultipleRaggedRowPredictionsError(Exception):
    pass


@dataclass(frozen=True)
class SameLineRaggedRowSchema:
    row_count_var: str
    prefix_fields: Tuple[str, ...]
    length_field_position: int
    values_name: str
    value_start_index: int
    first_format_line: int
    evidence_line_numbers: Tuple[int, ...]

    def __str__(self):
        return (
            "[SameLineRaggedRows: count={}, "
            "prefix={}, length_pos={}, values={}]"
        ).format(
            self.row_count_var,
            ",".join(self.prefix_fields),
            self.length_field_position,
            self.values_name,
        )


@dataclass
class SameLineRaggedRowPrediction:
    prefix_format: Format
    schema: SameLineRaggedRowSchema
    var_to_type: Dict[str, Type]
    sample_row_counts: Tuple[int, ...]

    def __str__(self):
        return (
            "[RaggedPrediction: prefix={}, rows={}]"
        ).format(
            self.prefix_format,
            self.schema,
        )


@dataclass(frozen=True)
class _IndexedWord:
    base: str
    indices: Tuple[str, ...]
    normalized: str


@dataclass(frozen=True)
class _LineCandidate:
    line_number: int
    outer_index: str
    prefix_fields: Tuple[str, ...]
    length_field_position: int
    length_base: str
    values_name: str
    value_start_index: int


_INDEXED_WORD_PATTERN = re.compile(
    r"""
    ^
    (?P<base>[A-Za-z][A-Za-z0-9]*)
    _
    (?:
        \{
            (?P<braced>[^{}]+)
        \}
        |
        (?P<plain>[A-Za-z0-9_]+)
    )
    $
    """,
    re.VERBOSE,
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]*$"
)


def _normalize_component(value: str) -> str:
    return re.sub(
        r"\s+",
        "",
        value,
    )


def _parse_indexed_word(
    value: str,
):
    normalized = _normalize_component(
        value
    )

    match = _INDEXED_WORD_PATTERN.fullmatch(
        normalized
    )

    if match is None:
        return None

    index_text = (
        match.group("braced")
        or match.group("plain")
    )

    return _IndexedWord(
        base=match.group("base"),
        indices=tuple(
            _normalize_component(part)
            for part in index_text.split(",")
        ),
        normalized=normalized,
    )


def _word_positions(line):
    return [
        (index, token)
        for index, token
        in enumerate(line.tokens)
        if token.kind == InputTokenKind.WORD
    ]


def _candidate_from_line(
    line,
    line_number: int,
):
    ellipsis_positions = [
        index
        for index, token
        in enumerate(line.tokens)
        if token.kind
        == InputTokenKind.ELLIPSIS
    ]

    for ellipsis_position in (
        ellipsis_positions
    ):
        left_position = None
        left_token = None
        right_token = None

        for index in range(
            ellipsis_position - 1,
            -1,
            -1,
        ):
            token = line.tokens[index]

            if token.kind == InputTokenKind.WORD:
                left_position = index
                left_token = token
                break

        for index in range(
            ellipsis_position + 1,
            len(line.tokens),
        ):
            token = line.tokens[index]

            if token.kind == InputTokenKind.WORD:
                right_token = token
                break

        if (
            left_position is None
            or left_token is None
            or right_token is None
        ):
            continue

        left = _parse_indexed_word(
            left_token.normalized_text
        )

        right = _parse_indexed_word(
            right_token.normalized_text
        )

        if left is None or right is None:
            continue

        if left.base != right.base:
            continue

        if (
            len(left.indices) != 2
            or len(right.indices) != 2
        ):
            continue

        outer_index = left.indices[0]

        if right.indices[0] != outer_index:
            continue

        if left.indices[1] not in {
            "0",
            "1",
        }:
            continue

        length_reference = (
            _parse_indexed_word(
                right.indices[1]
            )
        )

        if length_reference is None:
            continue

        if len(length_reference.indices) != 1:
            continue

        if (
            length_reference.indices[0]
            != outer_index
        ):
            continue

        prefix_tokens = [
            token
            for _, token in _word_positions(line)
            if _ < left_position
        ]

        if not prefix_tokens:
            continue

        prefix_references = [
            _parse_indexed_word(
                token.normalized_text
            )
            for token in prefix_tokens
        ]

        if any(
            reference is None
            for reference in prefix_references
        ):
            continue

        if any(
            len(reference.indices) != 1
            or reference.indices[0]
            != outer_index
            for reference in prefix_references
        ):
            continue

        prefix_fields = tuple(
            reference.base
            for reference in prefix_references
        )

        matching_length_positions = [
            index
            for index, reference
            in enumerate(prefix_references)
            if (
                reference.base
                == length_reference.base
            )
        ]

        if len(matching_length_positions) != 1:
            continue

        return _LineCandidate(
            line_number=line_number,
            outer_index=outer_index,
            prefix_fields=prefix_fields,
            length_field_position=(
                matching_length_positions[0]
            ),
            length_base=(
                length_reference.base
            ),
            values_name=left.base,
            value_start_index=int(
                left.indices[1]
            ),
        )

    return None


def detect_same_line_ragged_row_schemas(
    content: ProblemContent,
) -> List[SameLineRaggedRowSchema]:
    specification = (
        InputSpecification.from_problem_content(
            content
        )
    )

    if not specification.blocks:
        return []

    main_block = specification.blocks[0]
    grouped = {}

    for line_number, line in enumerate(
        main_block.lines,
        start=1,
    ):
        candidate = _candidate_from_line(
            line,
            line_number,
        )

        if candidate is None:
            continue

        key = (
            candidate.prefix_fields,
            candidate.length_field_position,
            candidate.length_base,
            candidate.values_name,
            candidate.value_start_index,
        )

        grouped.setdefault(
            key,
            [],
        ).append(candidate)

    schemas = []

    for (
        prefix_fields,
        length_field_position,
        length_base,
        values_name,
        value_start_index,
    ), candidates in grouped.items():
        if len(candidates) < 2:
            continue

        outer_indices = {
            candidate.outer_index
            for candidate in candidates
        }

        if not outer_indices.intersection({
            "0",
            "1",
        }):
            continue

        symbolic_endpoints = sorted(
            index
            for index in outer_indices
            if (
                index not in {"0", "1", "2"}
                and _IDENTIFIER_PATTERN.fullmatch(
                    index
                )
            )
        )

        if len(symbolic_endpoints) != 1:
            continue

        row_count_var = symbolic_endpoints[0]

        schemas.append(
            SameLineRaggedRowSchema(
                row_count_var=row_count_var,
                prefix_fields=prefix_fields,
                length_field_position=(
                    length_field_position
                ),
                values_name=values_name,
                value_start_index=(
                    value_start_index
                ),
                first_format_line=min(
                    candidate.line_number
                    for candidate in candidates
                ),
                evidence_line_numbers=tuple(
                    sorted(
                        candidate.line_number
                        for candidate
                        in candidates
                    )
                ),
            )
        )

    return schemas


def _simple_format_candidates(
    input_format_text: str,
):
    if not input_format_text.strip():
        return []

    try:
        tokenized_candidates = (
            search_formats_with_minimum_vars(
                input_format_text
            )
        )
    except NoFormatFoundError:
        return []

    results = []
    seen = set()

    for tokenized_candidate in (
        tokenized_candidates
    ):
        for to_1d_flag in (False, True):
            try:
                candidate = (
                    predict_simple_format(
                        tokenized_candidate.var_tokens,
                        to_1d_flag,
                    )
                )
            except (
                SimpleFormatPredictionFailedError
            ):
                continue

            signature = str(candidate)

            if signature in seen:
                continue

            seen.add(signature)
            results.append(candidate)

    return results


def _sample_lines(sample):
    return [
        line.split()
        for line in (
            raw_line.strip()
            for raw_line
            in sample.get_input().splitlines()
        )
        if line
    ]


def _line_boundary_for_token_count(
    lines,
    token_count: int,
):
    if token_count == 0:
        return 0

    consumed = 0

    for index, line in enumerate(lines):
        consumed += len(line)

        if consumed == token_count:
            return index + 1

        if consumed > token_count:
            return None

    return None


def _type_from_token(
    token: str,
) -> Type:
    if is_int(token):
        value = int(token)
    elif is_float(token):
        value = float(token)
    else:
        value = token

    return Type.from_py_type(
        type(value)
    )


def _merge_variable_type(
    var_to_type,
    variable_name: str,
    type_: Type,
):
    if variable_name in var_to_type:
        var_to_type[variable_name] = (
            var_to_type[
                variable_name
            ].intersect(type_)
        )
    else:
        var_to_type[variable_name] = type_


def _validate_prediction(
    prefix_format,
    schema,
    samples,
):
    merged_types = {}
    sample_row_counts = []

    for sample in samples:
        lines = _sample_lines(sample)
        flattened_tokens = [
            token
            for line in lines
            for token in line
        ]

        token_manager = TokenManager(
            flattened_tokens
        )

        prefix_predictor = TypePredictor(
            prefix_format
        )

        prefix_predictor.consume(
            token_manager
        )

        row_count = (
            prefix_predictor.get_actual_value(
                schema.row_count_var
            )
        )

        if (
            type(row_count) is not int
            or row_count <= 0
        ):
            raise NoRaggedRowPredictionError

        boundary = (
            _line_boundary_for_token_count(
                lines,
                token_manager._pos,
            )
        )

        if boundary is None:
            raise NoRaggedRowPredictionError

        if boundary + row_count > len(lines):
            raise NoRaggedRowPredictionError

        row_lines = lines[
            boundary:
            boundary + row_count
        ]

        sample_types = dict(
            prefix_predictor.get_typing_result()
        )

        for row in row_lines:
            prefix_count = len(
                schema.prefix_fields
            )

            if len(row) < prefix_count:
                raise NoRaggedRowPredictionError

            length_token = row[
                schema.length_field_position
            ]

            if not is_int(length_token):
                raise NoRaggedRowPredictionError

            declared_length = int(
                length_token
            )

            value_tokens = row[
                prefix_count:
            ]

            if (
                declared_length < 0
                or declared_length
                != len(value_tokens)
            ):
                raise NoRaggedRowPredictionError

            for field_name, token in zip(
                schema.prefix_fields,
                row[:prefix_count],
            ):
                _merge_variable_type(
                    sample_types,
                    field_name,
                    _type_from_token(token),
                )

            for token in value_tokens:
                _merge_variable_type(
                    sample_types,
                    schema.values_name,
                    _type_from_token(token),
                )

        if (
            sample_types.get(
                schema.prefix_fields[
                    schema.length_field_position
                ]
            )
            != Type.int
        ):
            raise NoRaggedRowPredictionError

        merged_types = merge_type_dicts(
            merged_types,
            sample_types,
        )

        sample_row_counts.append(
            row_count
        )

    return (
        merged_types,
        tuple(sample_row_counts),
    )


def predict_same_line_ragged_rows(
    content: ProblemContent,
) -> SameLineRaggedRowPrediction:
    samples = content.get_samples()

    if not samples:
        raise NoRaggedRowPredictionError

    schemas = (
        detect_same_line_ragged_row_schemas(
            content
        )
    )

    predictions = []
    seen = set()

    specification = (
        InputSpecification.from_problem_content(
            content
        )
    )

    if not specification.blocks:
        raise NoRaggedRowPredictionError

    main_lines = specification.blocks[0].lines

    for schema in schemas:
        prefix_text = "\n".join(
            line.raw_text
            for line in main_lines[
                :schema.first_format_line - 1
            ]
        )

        for prefix_format in (
            _simple_format_candidates(
                prefix_text
            )
        ):
            prefix_variable_names = {
                variable.name
                for variable
                in prefix_format.all_vars()
            }

            if (
                schema.row_count_var
                not in prefix_variable_names
            ):
                continue

            try:
                (
                    var_to_type,
                    sample_row_counts,
                ) = _validate_prediction(
                    prefix_format,
                    schema,
                    samples,
                )
            except (
                AssertionError,
                EvaluateError,
                InvalidLoopIndexError,
                InvalidLoopSizeError,
                KeyError,
                NoRaggedRowPredictionError,
                StopIteration,
                TooLessFetchesError,
                TooManyFetchesError,
                ValueError,
            ):
                continue

            signature = (
                str(prefix_format),
                str(schema),
            )

            if signature in seen:
                continue

            seen.add(signature)

            predictions.append(
                SameLineRaggedRowPrediction(
                    prefix_format=prefix_format,
                    schema=schema,
                    var_to_type=var_to_type,
                    sample_row_counts=(
                        sample_row_counts
                    ),
                )
            )

    if not predictions:
        raise NoRaggedRowPredictionError

    if len(predictions) > 1:
        raise (
            MultipleRaggedRowPredictionsError
        )

    return predictions[0]
