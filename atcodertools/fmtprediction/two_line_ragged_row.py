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
from atcodertools.fmtprediction.ragged_row import (
    _format_from_sequence,
    _line_boundary_for_token_count,
    _parse_indexed_word,
    _pattern_signatures,
    _simple_format_candidates,
)
from atcodertools.fmtprediction.token_manager import (
    TokenManager,
)


class NoTwoLineRaggedRowPredictionError(
    Exception
):
    pass


class MultipleTwoLineRaggedRowPredictionsError(
    Exception
):
    pass


@dataclass(frozen=True)
class TwoLineRaggedRowSchema:
    row_count_var: str
    prefix_fields: Tuple[str, ...]
    length_field_position: int
    values_name: str
    value_start_index: int
    first_format_line: int
    evidence_line_numbers: Tuple[int, ...]

    def __str__(self):
        return (
            "[TwoLineRaggedRows: count={}, "
            "length={}, values={}]"
        ).format(
            self.row_count_var,
            self.prefix_fields[0],
            self.values_name,
        )


@dataclass
class TwoLineRaggedRowPrediction:
    prefix_format: Format
    suffix_format: Format
    schema: TwoLineRaggedRowSchema
    var_to_type: Dict[str, Type]
    sample_row_counts: Tuple[int, ...]


@dataclass(frozen=True)
class _PairCandidate:
    length_line_number: int
    value_line_number: int
    outer_index: str
    length_base: str
    values_name: str
    value_start_index: int


_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]*$"
)


def _word_tokens(line):
    return [
        token
        for token in line.tokens
        if token.kind == InputTokenKind.WORD
    ]


def _candidate_from_pair(
    length_line,
    value_line,
    length_line_number,
):
    length_words = _word_tokens(
        length_line
    )

    if len(length_words) != 1:
        return None

    length_reference = (
        _parse_indexed_word(
            length_words[0]
            .normalized_text
        )
    )

    if (
        length_reference is None
        or len(
            length_reference.indices
        ) != 1
    ):
        return None

    ellipsis_positions = [
        index
        for index, token
        in enumerate(value_line.tokens)
        if token.kind
        == InputTokenKind.ELLIPSIS
    ]

    for ellipsis_position in (
        ellipsis_positions
    ):
        left = None
        right = None

        for index in range(
            ellipsis_position - 1,
            -1,
            -1,
        ):
            token = value_line.tokens[index]

            if token.kind == InputTokenKind.WORD:
                left = _parse_indexed_word(
                    token.normalized_text
                )
                break

        for index in range(
            ellipsis_position + 1,
            len(value_line.tokens),
        ):
            token = value_line.tokens[index]

            if token.kind == InputTokenKind.WORD:
                right = _parse_indexed_word(
                    token.normalized_text
                )
                break

        if left is None or right is None:
            continue

        if (
            left.base != right.base
            or len(left.indices) != 2
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

        right_length = _parse_indexed_word(
            right.indices[1]
        )

        if (
            right_length is None
            or len(
                right_length.indices
            ) != 1
        ):
            continue

        if (
            length_reference.base
            != right_length.base
            or length_reference.indices[0]
            != outer_index
            or right_length.indices[0]
            != outer_index
        ):
            continue

        return _PairCandidate(
            length_line_number=(
                length_line_number
            ),
            value_line_number=(
                length_line_number + 1
            ),
            outer_index=outer_index,
            length_base=(
                length_reference.base
            ),
            values_name=left.base,
            value_start_index=int(
                left.indices[1]
            ),
        )

    return None


def detect_two_line_ragged_row_schemas(
    content: ProblemContent,
) -> List[TwoLineRaggedRowSchema]:
    specification = (
        InputSpecification.from_problem_content(
            content
        )
    )

    if not specification.blocks:
        return []

    lines = specification.blocks[0].lines
    grouped = {}

    for index in range(
        len(lines) - 1
    ):
        candidate = _candidate_from_pair(
            lines[index],
            lines[index + 1],
            index + 1,
        )

        if candidate is None:
            continue

        key = (
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
                index not in {
                    "0",
                    "1",
                    "2",
                }
                and _IDENTIFIER_PATTERN.fullmatch(
                    index
                )
            )
        )

        if len(symbolic_endpoints) != 1:
            continue

        row_count_var = (
            symbolic_endpoints[0]
        )

        evidence = []

        for candidate in candidates:
            evidence.extend(
                (
                    candidate.length_line_number,
                    candidate.value_line_number,
                )
            )

        schemas.append(
            TwoLineRaggedRowSchema(
                row_count_var=row_count_var,
                prefix_fields=(
                    length_base,
                ),
                length_field_position=0,
                values_name=values_name,
                value_start_index=(
                    value_start_index
                ),
                first_format_line=min(
                    candidate.length_line_number
                    for candidate in candidates
                ),
                evidence_line_numbers=tuple(
                    sorted(set(evidence))
                ),
            )
        )

    return schemas


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
    name,
    type_,
):
    if name in var_to_type:
        var_to_type[name] = (
            var_to_type[name]
            .intersect(type_)
        )
    else:
        var_to_type[name] = type_


def _validate_prediction(
    prefix_format,
    schema,
    samples,
):
    merged_types = {}
    row_counts = []

    for sample in samples:
        lines = _sample_lines(sample)

        flattened_tokens = [
            token
            for line in lines
            for token in line
        ]

        manager = TokenManager(
            flattened_tokens
        )

        predictor = TypePredictor(
            prefix_format
        )

        predictor.consume(manager)

        row_count = predictor.get_actual_value(
            schema.row_count_var
        )

        if (
            type(row_count) is not int
            or row_count <= 0
        ):
            raise (
                NoTwoLineRaggedRowPredictionError
            )

        boundary = (
            _line_boundary_for_token_count(
                lines,
                manager._pos,
            )
        )

        if boundary is None:
            raise (
                NoTwoLineRaggedRowPredictionError
            )

        required_end = (
            boundary + 2 * row_count
        )

        if required_end > len(lines):
            raise (
                NoTwoLineRaggedRowPredictionError
            )

        sample_types = dict(
            predictor.get_typing_result()
        )

        for row_index in range(
            row_count
        ):
            length_line = lines[
                boundary + 2 * row_index
            ]

            values_line = lines[
                boundary + 2 * row_index + 1
            ]

            if (
                len(length_line) != 1
                or not is_int(
                    length_line[0]
                )
            ):
                raise (
                    NoTwoLineRaggedRowPredictionError
                )

            declared_length = int(
                length_line[0]
            )

            if (
                declared_length < 0
                or declared_length
                != len(values_line)
            ):
                raise (
                    NoTwoLineRaggedRowPredictionError
                )

            _merge_variable_type(
                sample_types,
                schema.prefix_fields[0],
                Type.int,
            )

            for token in values_line:
                _merge_variable_type(
                    sample_types,
                    schema.values_name,
                    _type_from_token(token),
                )

        merged_types = merge_type_dicts(
            merged_types,
            sample_types,
        )

        row_counts.append(row_count)

    return (
        merged_types,
        tuple(row_counts),
    )


def _predict_suffix_format(
    prefix_format,
    schema,
    samples,
    main_lines,
):
    prefix_text = "\n".join(
        line.raw_text
        for line in main_lines[
            :schema.first_format_line - 1
        ]
    )

    suffix_text = "\n".join(
        line.raw_text
        for line in main_lines[
            max(
                schema.evidence_line_numbers
            ):
        ]
    )

    non_ragged_text = "\n".join(
        part
        for part in (
            prefix_text,
            suffix_text,
        )
        if part.strip()
    )

    prefix_signatures = (
        _pattern_signatures(
            prefix_format
        )
    )

    prefix_count = len(
        prefix_signatures
    )

    valid_candidates = []
    seen = set()

    for candidate in (
        _simple_format_candidates(
            non_ragged_text
        )
    ):
        candidate_signatures = (
            _pattern_signatures(
                candidate
            )
        )

        if (
            candidate_signatures[
                :prefix_count
            ]
            != prefix_signatures
        ):
            continue

        merged_types = {}
        valid = True

        for sample in samples:
            lines = _sample_lines(sample)

            flattened_tokens = [
                token
                for line in lines
                for token in line
            ]

            try:
                prefix_manager = TokenManager(
                    flattened_tokens
                )

                prefix_predictor = (
                    TypePredictor(
                        prefix_format
                    )
                )

                prefix_predictor.consume(
                    prefix_manager
                )

                row_count = (
                    prefix_predictor
                    .get_actual_value(
                        schema.row_count_var
                    )
                )

                boundary = (
                    _line_boundary_for_token_count(
                        lines,
                        prefix_manager._pos,
                    )
                )

                if (
                    boundary is None
                    or type(row_count) is not int
                ):
                    raise ValueError

                non_ragged_lines = (
                    lines[:boundary]
                    + lines[
                        boundary
                        + 2 * row_count:
                    ]
                )

                tokens = [
                    token
                    for line in non_ragged_lines
                    for token in line
                ]

                manager = TokenManager(tokens)
                predictor = TypePredictor(
                    candidate
                )

                predictor.consume(manager)

                if manager._pos != len(tokens):
                    raise ValueError

                merged_types = merge_type_dicts(
                    merged_types,
                    predictor.get_typing_result(),
                )

            except (
                AssertionError,
                EvaluateError,
                InvalidLoopIndexError,
                InvalidLoopSizeError,
                KeyError,
                StopIteration,
                TooLessFetchesError,
                TooManyFetchesError,
                ValueError,
            ):
                valid = False
                break

        if not valid:
            continue

        suffix_format = _format_from_sequence(
            candidate.sequence[
                prefix_count:
            ]
        )

        signature = str(suffix_format)

        if signature in seen:
            continue

        seen.add(signature)

        valid_candidates.append(
            (
                suffix_format,
                merged_types,
            )
        )

    if len(valid_candidates) != 1:
        raise (
            NoTwoLineRaggedRowPredictionError
        )

    return valid_candidates[0]


def predict_two_line_ragged_rows(
    content: ProblemContent,
) -> TwoLineRaggedRowPrediction:
    samples = content.get_samples()

    if not samples:
        raise (
            NoTwoLineRaggedRowPredictionError
        )

    schemas = (
        detect_two_line_ragged_row_schemas(
            content
        )
    )

    specification = (
        InputSpecification.from_problem_content(
            content
        )
    )

    if not specification.blocks:
        raise (
            NoTwoLineRaggedRowPredictionError
        )

    main_lines = specification.blocks[0].lines
    predictions = []
    seen = set()

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
            variable_names = {
                variable.name
                for variable
                in prefix_format.all_vars()
            }

            if (
                schema.row_count_var
                not in variable_names
            ):
                continue

            try:
                (
                    var_to_type,
                    row_counts,
                ) = _validate_prediction(
                    prefix_format,
                    schema,
                    samples,
                )

                (
                    suffix_format,
                    suffix_types,
                ) = _predict_suffix_format(
                    prefix_format,
                    schema,
                    samples,
                    main_lines,
                )

                var_to_type = merge_type_dicts(
                    var_to_type,
                    suffix_types,
                )

            except (
                AssertionError,
                EvaluateError,
                InvalidLoopIndexError,
                InvalidLoopSizeError,
                KeyError,
                NoTwoLineRaggedRowPredictionError,
                StopIteration,
                TooLessFetchesError,
                TooManyFetchesError,
                ValueError,
            ):
                continue

            signature = (
                str(prefix_format),
                str(schema),
                str(suffix_format),
            )

            if signature in seen:
                continue

            seen.add(signature)

            predictions.append(
                TwoLineRaggedRowPrediction(
                    prefix_format=prefix_format,
                    suffix_format=suffix_format,
                    schema=schema,
                    var_to_type=var_to_type,
                    sample_row_counts=(
                        row_counts
                    ),
                )
            )

    if not predictions:
        raise (
            NoTwoLineRaggedRowPredictionError
        )

    if len(predictions) > 1:
        raise (
            MultipleTwoLineRaggedRowPredictionsError
        )

    return predictions[0]
