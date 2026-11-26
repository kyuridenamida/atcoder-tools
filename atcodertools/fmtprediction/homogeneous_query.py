from atcodertools.fmtprediction.query_ir_producer_seams import (
    _create_homogeneous_prediction_with_shadow,
)

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction import tagged_query
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryArgument,
    TaggedQueryValueType,
)
from atcodertools.fmtprediction.models.type import Type

_homogeneous_prediction_shadow = (
    _create_homogeneous_prediction_with_shadow
)


class NoHomogeneousQueryPredictionError(
    Exception
):
    pass


class MultipleHomogeneousQueryPredictionsError(
    Exception
):
    pass


@dataclass(frozen=True)
class HomogeneousQueryPrediction:
    format: HomogeneousQueryFormat
    var_to_type: Dict[str, Type]
    sample_query_counts: Tuple[int, ...]


def _extract_argument_names(
    blocks,
) -> Tuple[str, ...]:
    if (
        not isinstance(blocks, list)
        or len(blocks) != 2
    ):
        raise NoHomogeneousQueryPredictionError

    definition_block = blocks[1]

    if not isinstance(definition_block, str):
        raise NoHomogeneousQueryPredictionError

    rows = []

    for segment in tagged_query._line_segments(
        definition_block
    ):
        tokens = tuple(
            tagged_query._TOKEN_PATTERN.findall(
                segment
            )
        )

        if not tokens:
            continue

        if tagged_query._COMPARISON_PATTERN.search(
            segment
        ):
            raise NoHomogeneousQueryPredictionError

        rows.append(tokens)

    if len(rows) != 1:
        raise NoHomogeneousQueryPredictionError

    argument_names = rows[0]

    if not 1 <= len(argument_names) <= 6:
        raise NoHomogeneousQueryPredictionError

    if not all(
        tagged_query._IDENTIFIER_PATTERN.fullmatch(
            argument
        )
        is not None
        for argument in argument_names
    ):
        raise NoHomogeneousQueryPredictionError

    if (
        len(argument_names)
        != len(set(argument_names))
    ):
        raise NoHomogeneousQueryPredictionError

    return argument_names


def _create_prediction(
    prefix_format,
    query_count_var: str,
    argument_names: Tuple[str, ...],
    samples,
) -> HomogeneousQueryPrediction:
    observed_types: List[
        Set[TaggedQueryValueType]
    ] = [
        set()
        for _ in argument_names
    ]

    sample_query_counts = []
    prefix_typings = []

    for sample in samples:
        lines = tagged_query._sample_lines(
            sample
        )

        flattened_tokens = [
            token
            for line in lines
            for token in line
        ]

        manager = tagged_query.TokenManager(
            flattened_tokens
        )

        predictor = tagged_query.TypePredictor(
            prefix_format
        )

        predictor.consume(manager)

        prefix_typings.append(
            predictor.get_typing_result()
        )

        boundary = (
            tagged_query
            ._line_boundary_for_token_count(
                lines,
                manager._pos,
            )
        )

        if boundary is None:
            raise NoHomogeneousQueryPredictionError

        query_count = (
            predictor.get_actual_value(
                query_count_var
            )
        )

        if (
            type(query_count) is not int
            or query_count <= 0
        ):
            raise NoHomogeneousQueryPredictionError

        if (
            boundary + query_count
            != len(lines)
        ):
            raise NoHomogeneousQueryPredictionError

        for row in lines[boundary:]:
            if len(row) != len(argument_names):
                raise NoHomogeneousQueryPredictionError

            for position, token in enumerate(row):
                observed_types[position].add(
                    tagged_query._classify_token(
                        token
                    )
                )

        sample_query_counts.append(
            query_count
        )

    if not prefix_typings:
        raise NoHomogeneousQueryPredictionError

    var_to_type = {}

    for typing in prefix_typings:
        tagged_query.merge_type_dicts(
            var_to_type,
            typing,
        )

    expected_prefix_names = {
        variable.name
        for variable
        in prefix_format.all_vars()
    }

    if set(var_to_type) != expected_prefix_names:
        raise NoHomogeneousQueryPredictionError

    arguments = tuple(
        TaggedQueryArgument(
            name=name,
            type=tagged_query._merge_types(
                observed_types[position]
            ),
        )
        for position, name
        in enumerate(argument_names)
    )

    prefix_names = {
        variable.name
        for variable
        in prefix_format.all_vars()
    }

    homogeneous_argument_names = {
        argument.name
        for argument in arguments
    }

    if prefix_names & homogeneous_argument_names:
        raise NoHomogeneousQueryPredictionError

    if tagged_query._RESERVED_NAMES & (
        prefix_names
        | homogeneous_argument_names
    ):
        raise NoHomogeneousQueryPredictionError

    return HomogeneousQueryPrediction(
        format=HomogeneousQueryFormat(
            prefix_format=prefix_format,
            query_count_var=query_count_var,
            arguments=arguments,
        ),
        var_to_type=var_to_type,
        sample_query_counts=tuple(
            sample_query_counts
        ),
    )


def predict_homogeneous_queries(
    content: ProblemContent,
) -> HomogeneousQueryPrediction:
    samples = content.get_samples()

    if not samples:
        raise NoHomogeneousQueryPredictionError

    blocks = getattr(
        content,
        "input_format_blocks",
        None,
    )

    argument_names = _extract_argument_names(
        blocks
    )

    query_count_candidates = (
        tagged_query._query_count_candidates(
            content
        )
    )

    if not query_count_candidates:
        raise NoHomogeneousQueryPredictionError

    specification = (
        tagged_query.InputSpecification
        .from_problem_content(content)
    )

    if not specification.blocks:
        raise NoHomogeneousQueryPredictionError

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
            for line in main_lines[:prefix_end]
        )

        for prefix_format in (
            tagged_query._simple_format_candidates(
                prefix_text
            )
        ):
            scalar_names = (
                tagged_query._scalar_variable_names(
                    prefix_format
                )
            )

            for query_count_var in sorted(
                scalar_names
                & query_count_candidates
            ):
                try:
                    prediction = (
                        _homogeneous_prediction_shadow(
                            _create_prediction,
                            prefix_format,
                            query_count_var,
                            argument_names,
                            samples,
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
                            argument.name,
                            argument.type.value,
                        )
                        for argument
                        in prediction
                        .format
                        .arguments
                    ),
                )

                if signature in seen:
                    continue

                seen.add(signature)
                predictions.append(
                    prediction
                )

    if not predictions:
        raise NoHomogeneousQueryPredictionError

    if len(predictions) > 1:
        raise (
            MultipleHomogeneousQueryPredictionsError
        )

    return predictions[0]
