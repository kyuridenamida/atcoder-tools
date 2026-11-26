from __future__ import annotations

from dataclasses import is_dataclass
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple

from atcodertools.fmtprediction.query_ir_lowering import (
    object_state,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowObserver,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowValidationError,
)


TargetSpec = Tuple[str, Dict[str, str]]


_PR324_TARGET_SPECS: Dict[
    Tuple[str, str],
    TargetSpec,
] = {
    (
        'atcodertools.fmtprediction.models.tagged_query_format',
        'TaggedQueryArgument',
    ): (
        'COMMON_TAGGED',
        {
            'name':
                'FIELD_NAME',
            'type':
                'OPAQUE_PRESERVED',
        },
    ),
    (
        'atcodertools.fmtprediction.models.tagged_query_format',
        'TaggedQueryFormat',
    ): (
        'COMMON_TAGGED',
        {
            'prefix_format':
                'PREFIX_FORMAT',
            'query_collection_name':
                'OPAQUE_PRESERVED',
            'query_count_var':
                'COUNT_REFERENCE',
            'variants':
                'VARIANTS',
        },
    ),
    (
        'atcodertools.fmtprediction.models.tagged_query_format',
        'TaggedQueryVariant',
    ): (
        'COMMON_TAGGED',
        {
            'arguments':
                'FIELDS',
            'tag':
                'TAG',
        },
    ),
    (
        'atcodertools.fmtprediction.tagged_query',
        'TaggedQueryPrediction',
    ): (
        'COMMON_TAGGED',
        {
            'format':
                'FORMAT',
            'sample_query_counts':
                'COUNT_REFERENCE',
            'var_to_type':
                'OPAQUE_PRESERVED',
        },
    ),
}


def _iter_query_children(
    value: Any,
) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, current in value.items():
            yield key
            yield current
        return

    if isinstance(
        value,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        yield from value
        return

    value_type = type(value)
    type_key = (
        value_type.__module__,
        value_type.__qualname__,
    )

    if (
        type_key in _PR324_TARGET_SPECS
        or is_dataclass(value)
        or value_type.__module__.startswith(
            "atcodertools.fmtprediction"
        )
    ):
        yield from object_state(value).values()


def _observe_reachable_query_targets(
    result: Any,
    observer: QueryIRShadowObserver,
) -> int:
    stack = [result]
    seen = set()
    observed = 0

    while stack:
        value = stack.pop()

        if value is None or isinstance(
            value,
            (
                bool,
                int,
                float,
                str,
                bytes,
                type,
            ),
        ):
            continue

        value_id = id(value)

        if value_id in seen:
            continue

        seen.add(value_id)

        value_type = type(value)
        type_key = (
            value_type.__module__,
            value_type.__qualname__,
        )

        if type_key in _PR324_TARGET_SPECS:
            category, field_roles = (
                _PR324_TARGET_SPECS[type_key]
            )
            returned = observer.observe(
                instance=value,
                category=category,
                field_roles=field_roles,
            )

            if returned is not value:
                raise QueryIRShadowValidationError(
                    "QUERY_IR_SHADOW_RESULT_IDENTITY_CHANGED"
                )

            observed += 1

        stack.extend(
            _iter_query_children(value)
        )

    return observed


def _require_observed_target(
    result: Any,
    observer: Optional[
        QueryIRShadowObserver
    ],
) -> Any:
    if observer is None:
        return result

    observed = _observe_reachable_query_targets(
        result,
        observer,
    )

    if observed == 0:
        raise QueryIRShadowValidationError(
            "QUERY_IR_SHADOW_TARGET_NOT_REACHABLE"
        )

    return result


def _create_tagged_query_typed_format_with_shadow(
    producer: Any,
    format_: Any,
    var_to_type: Any,
    *,
    observer: Optional[
        QueryIRShadowObserver
    ] = None,
) -> Any:
    result = producer(
        format_,
        var_to_type,
    )

    return _require_observed_target(
        result,
        observer,
    )


def _create_prediction_with_shadow(
    producer: Any,
    prefix_format: Any,
    query_count_var: str,
    definitions: Any,
    samples: Any,
    *,
    observer: Optional[
        QueryIRShadowObserver
    ] = None,
) -> Any:
    result = producer(
        prefix_format,
        query_count_var,
        definitions,
        samples,
    )

    return _require_observed_target(
        result,
        observer,
    )
