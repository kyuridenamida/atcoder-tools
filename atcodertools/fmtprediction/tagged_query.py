from atcodertools.fmtprediction.query_ir_producer_seams import (
    _create_prediction_with_shadow,
)

from dataclasses import dataclass
import html
import re
from typing import Dict, List, Sequence, Set, Tuple

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.models.input_specification import (
    InputSpecification,
    InputTokenKind,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryArgument,
    TaggedQueryFormat,
    TaggedQueryValueType,
    TaggedQueryVariant,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.predict_types import (
    TypePredictor,
    is_float,
    is_int,
    merge_type_dicts,
)
from atcodertools.fmtprediction.ragged_row import (
    _line_boundary_for_token_count,
    _parse_indexed_word,
    _simple_format_candidates,
)
from atcodertools.fmtprediction.token_manager import (
    TokenManager,
)


class NoTaggedQueryPredictionError(Exception):
    pass


class MultipleTaggedQueryPredictionsError(Exception):
    pass


@dataclass(frozen=True)
class TaggedQueryPrediction:
    format: TaggedQueryFormat
    var_to_type: Dict[str, Type]
    sample_query_counts: Tuple[int, ...]


@dataclass(frozen=True)
class _VariantDefinition:
    tag: int
    argument_names: Tuple[str, ...]


_HTML_BREAK_PATTERN = re.compile(
    r"(?i)<br\s*/?>"
)

_HTML_BLOCK_END_PATTERN = re.compile(
    r"(?i)</(?:p|li|div|tr|td|section|pre)>"
)

_HTML_TAG_PATTERN = re.compile(
    r"<[^>]*>"
)

_TEX_WRAPPER_PATTERN = re.compile(
    (
        r"\\(?:"
        r"mathrm|text|mathtt|mathbf|"
        r"mathit|operatorname"
        r")\s*\{([^{}]*)\}"
    )
)

_TOKEN_PATTERN = re.compile(
    r"[A-Za-z][A-Za-z0-9_]*|[+-]?\d+"
)

_INTEGER_PATTERN = re.compile(
    r"[+-]?\d+"
)

_IDENTIFIER_PATTERN = re.compile(
    r"[A-Za-z][A-Za-z0-9_]*"
)

_COMPARISON_PATTERN = re.compile(
    r"(?:<=|>=|==|\\leq|\\geq|≤|≥|∈)"
)

_PLACEHOLDER_BASES = {
    "query",
    "queries",
    "operation",
    "operations",
    "command",
    "commands",
    "request",
    "requests",
    "op",
}

_RESERVED_NAMES = {
    "queries",
    "query",
    "tag",
    "args",
}


def _sample_lines(sample) -> List[List[str]]:
    return [
        line.split()
        for line in (
            raw_line.strip()
            for raw_line
            in sample.get_input().splitlines()
        )
        if line
    ]


def _scalar_variable_names(
    format_,
) -> Set[str]:
    return {
        variable.name
        for variable in format_.all_vars()
        if variable.dim_num() == 0
    }


def _unwrap_tex(text: str) -> str:
    previous = None

    while previous != text:
        previous = text

        text = _TEX_WRAPPER_PATTERN.sub(
            r"\1",
            text,
        )

    return text


def _normalize_block(text: str) -> str:
    text = html.unescape(text)

    text = _HTML_BREAK_PATTERN.sub(
        "\n",
        text,
    )

    text = _HTML_BLOCK_END_PATTERN.sub(
        "\n",
        text,
    )

    text = _HTML_TAG_PATTERN.sub(
        " ",
        text,
    )

    text = text.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    text = _unwrap_tex(text)

    for marker in (
        r"\(",
        r"\)",
        r"\[",
        r"\]",
        "$",
        "`",
    ):
        text = text.replace(
            marker,
            " ",
        )

    text = text.replace(
        r"\\",
        "\n",
    )

    text = text.replace(
        r"\cr",
        "\n",
    )

    text = text.replace(
        r"\newline",
        "\n",
    )

    text = re.sub(
        r"_\{([^{}]+)\}",
        r"_\1",
        text,
    )

    text = text.replace(
        "{",
        "",
    ).replace(
        "}",
        "",
    )

    text = re.sub(
        r"\\([A-Za-z]+)",
        r" \1 ",
        text,
    )

    return text


def _line_segments(
    text: str,
) -> List[str]:
    segments = []

    for raw_line in (
        _normalize_block(text)
        .splitlines()
    ):
        for cell in raw_line.split("&"):
            cleaned = re.sub(
                r"\s+",
                " ",
                cell,
            ).strip()

            if cleaned:
                segments.append(cleaned)

    return segments


def _extract_variant_definitions(
    blocks: Sequence[str],
) -> Tuple[_VariantDefinition, ...]:
    by_tag = {}

    for block in blocks:
        if not isinstance(block, str):
            raise NoTaggedQueryPredictionError

        for segment in _line_segments(block):
            semantic_tokens = (
                _TOKEN_PATTERN.findall(
                    segment
                )
            )

            if not semantic_tokens:
                continue

            first = semantic_tokens[0]

            if not _INTEGER_PATTERN.fullmatch(
                first
            ):
                continue

            tag = int(first)

            if not 1 <= tag <= 3:
                continue

            if _COMPARISON_PATTERN.search(
                segment
            ):
                continue

            arguments = tuple(
                semantic_tokens[1:]
            )

            if len(arguments) > 3:
                continue

            if not all(
                _IDENTIFIER_PATTERN.fullmatch(
                    argument
                )
                is not None
                for argument in arguments
            ):
                continue

            by_tag.setdefault(
                tag,
                [],
            ).append(arguments)

    if not 2 <= len(by_tag) <= 3:
        raise NoTaggedQueryPredictionError

    tags = sorted(by_tag)

    if tags != list(
        range(
            1,
            tags[-1] + 1,
        )
    ):
        raise NoTaggedQueryPredictionError

    definitions = []

    for tag in tags:
        unique_arguments = set(
            by_tag[tag]
        )

        if len(unique_arguments) != 1:
            raise NoTaggedQueryPredictionError

        definitions.append(
            _VariantDefinition(
                tag=tag,
                argument_names=next(
                    iter(unique_arguments)
                ),
            )
        )

    return tuple(definitions)


def _query_count_candidates(
    content: ProblemContent,
) -> Set[str]:
    specification = (
        InputSpecification
        .from_problem_content(content)
    )

    if not specification.blocks:
        return set()

    candidates = set()

    for line in specification.blocks[0].lines:
        for token in line.tokens:
            if token.kind != InputTokenKind.WORD:
                continue

            reference = _parse_indexed_word(
                token.normalized_text
            )

            if reference is None:
                continue

            if (
                reference.base.lower()
                not in _PLACEHOLDER_BASES
            ):
                continue

            if len(reference.indices) != 1:
                continue

            index = reference.indices[0]

            if index in {
                "0",
                "1",
                "2",
                "i",
                "j",
                "k",
            }:
                continue

            if (
                _IDENTIFIER_PATTERN.fullmatch(
                    index
                )
                is None
            ):
                continue

            candidates.add(index)

    return candidates


def _classify_token(
    token: str,
) -> TaggedQueryValueType:
    if is_int(token):
        return TaggedQueryValueType.INT

    if is_float(token):
        return TaggedQueryValueType.FLOAT

    return TaggedQueryValueType.STRING


def _merge_types(
    values: Set[TaggedQueryValueType],
) -> TaggedQueryValueType:
    if values == {
        TaggedQueryValueType.INT
    }:
        return TaggedQueryValueType.INT

    if values and values.issubset({
        TaggedQueryValueType.INT,
        TaggedQueryValueType.FLOAT,
    }):
        return TaggedQueryValueType.FLOAT

    if values == {
        TaggedQueryValueType.STRING
    }:
        return TaggedQueryValueType.STRING

    raise NoTaggedQueryPredictionError


def _create_prediction(
    prefix_format,
    query_count_var: str,
    definitions: Tuple[
        _VariantDefinition,
        ...,
    ],
    samples,
) -> TaggedQueryPrediction:
    definitions_by_tag = {
        str(definition.tag): definition
        for definition in definitions
    }

    observed_types: Dict[
        str,
        List[
            Set[TaggedQueryValueType]
        ],
    ] = {
        tag: [
            set()
            for _ in definition.argument_names
        ]
        for tag, definition
        in definitions_by_tag.items()
    }

    observed_tags = set()
    sample_query_counts = []
    prefix_typings = []

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

        prefix_typings.append(
            predictor.get_typing_result()
        )

        boundary = (
            _line_boundary_for_token_count(
                lines,
                manager._pos,
            )
        )

        if boundary is None:
            raise NoTaggedQueryPredictionError

        query_count = (
            predictor.get_actual_value(
                query_count_var
            )
        )

        if (
            type(query_count) is not int
            or query_count <= 0
        ):
            raise NoTaggedQueryPredictionError

        if (
            boundary + query_count
            != len(lines)
        ):
            raise NoTaggedQueryPredictionError

        for row in lines[boundary:]:
            if not row:
                raise NoTaggedQueryPredictionError

            tag = row[0]

            definition = (
                definitions_by_tag.get(tag)
            )

            if definition is None:
                raise NoTaggedQueryPredictionError

            arguments = row[1:]

            if (
                len(arguments)
                != len(
                    definition.argument_names
                )
            ):
                raise NoTaggedQueryPredictionError

            observed_tags.add(tag)

            for position, token in enumerate(
                arguments
            ):
                observed_types[
                    tag
                ][position].add(
                    _classify_token(token)
                )

        sample_query_counts.append(
            query_count
        )

    if observed_tags != set(
        definitions_by_tag
    ):
        raise NoTaggedQueryPredictionError

    if not prefix_typings:
        raise NoTaggedQueryPredictionError

    var_to_type = {}

    for typing in prefix_typings:
        merge_type_dicts(
            var_to_type,
            typing,
        )

    expected_prefix_names = {
        variable.name
        for variable
        in prefix_format.all_vars()
    }

    if set(var_to_type) != expected_prefix_names:
        raise NoTaggedQueryPredictionError

    variants = []

    for definition in definitions:
        tag = str(definition.tag)

        arguments = tuple(
            TaggedQueryArgument(
                name=name,
                type=_merge_types(
                    observed_types[
                        tag
                    ][position]
                ),
            )
            for position, name
            in enumerate(
                definition.argument_names
            )
        )

        variants.append(
            TaggedQueryVariant(
                tag=definition.tag,
                arguments=arguments,
            )
        )

    prefix_names = {
        variable.name
        for variable
        in prefix_format.all_vars()
    }

    argument_names = {
        argument.name
        for variant in variants
        for argument in variant.arguments
    }

    if prefix_names & argument_names:
        raise NoTaggedQueryPredictionError

    if _RESERVED_NAMES & (
        prefix_names | argument_names
    ):
        raise NoTaggedQueryPredictionError

    return TaggedQueryPrediction(
        format=TaggedQueryFormat(
            prefix_format=prefix_format,
            query_count_var=query_count_var,
            variants=tuple(variants),
        ),
        var_to_type=var_to_type,
        sample_query_counts=tuple(
            sample_query_counts
        ),
    )


def predict_tagged_queries(
    content: ProblemContent,
) -> TaggedQueryPrediction:
    samples = content.get_samples()

    if not samples:
        raise NoTaggedQueryPredictionError

    blocks = getattr(
        content,
        "input_format_blocks",
        None,
    )

    if (
        not isinstance(blocks, list)
        or not blocks
    ):
        raise NoTaggedQueryPredictionError

    definitions = (
        _extract_variant_definitions(
            blocks
        )
    )

    query_count_candidates = (
        _query_count_candidates(content)
    )

    use_scalar_fallback = not query_count_candidates

    specification = (
        InputSpecification
        .from_problem_content(content)
    )

    if not specification.blocks:
        raise NoTaggedQueryPredictionError

    main_lines = (
        specification.blocks[0].lines
    )

    predictions = []
    seen = set()

    for prefix_end in range(
        1,
        len(main_lines) + 1,
    ):
        prefix_text = "\n".join(
            line.raw_text
            for line in main_lines[
                :prefix_end
            ]
        )

        for prefix_format in (
            _simple_format_candidates(
                prefix_text
            )
        ):
            scalar_names = (
                _scalar_variable_names(
                    prefix_format
                )
            )

            candidate_names = (
                scalar_names
                if use_scalar_fallback
                else scalar_names & query_count_candidates
            )
            for query_count_var in sorted(
                candidate_names
            ):
                try:
                    prediction = (
                        (
                            _create_prediction_with_shadow(
                                _create_prediction,
                                prefix_format,
                                query_count_var,
                                definitions,
                                samples,
                            )
                        )
                    )
                except Exception:
                    continue

                signature = (
                    str(
                        prediction
                        .format
                        .prefix_format
                    ),
                    prediction
                    .format
                    .query_count_var,
                    tuple(
                        (
                            variant.tag,
                            tuple(
                                (
                                    argument.name,
                                    argument.type.value,
                                )
                                for argument
                                in variant.arguments
                            ),
                        )
                        for variant
                        in prediction
                        .format
                        .variants
                    ),
                )

                if signature in seen:
                    continue

                seen.add(signature)
                predictions.append(
                    prediction
                )

    if not predictions:
        raise NoTaggedQueryPredictionError

    if len(predictions) > 1:
        raise (
            MultipleTaggedQueryPredictionsError
        )

    return predictions[0]
