from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Tuple
from typing import Union

from atcodertools.fmtprediction.query_ir_lowering import (
    AdapterState,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    PostInitModelIR,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    decode_value,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    encode_value,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    object_state,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    snapshot_value,
)


@dataclass(frozen=True)
class ScalarReference:
    name: str


@dataclass(frozen=True)
class QueryFieldSpec:
    name: str
    value_type: Any


@dataclass(frozen=True)
class QueryVariantSpec:
    tag_value: Any
    fields: Tuple[QueryFieldSpec, ...]


@dataclass(frozen=True)
class TaggedQuerySpec:
    prefix_format: Any
    count: ScalarReference
    variants: Tuple[QueryVariantSpec, ...]


@dataclass(frozen=True)
class HomogeneousQuerySpec:
    prefix_format: Any
    count: ScalarReference
    fields: Tuple[QueryFieldSpec, ...]


QueryBodySpec = Union[
    TaggedQuerySpec,
    HomogeneousQuerySpec,
]


@dataclass(frozen=True)
class QueryInputSpec:
    body: QueryBodySpec


@dataclass(frozen=True)
class SemanticFieldIR:
    role: str
    source_name: str
    value: Any


@dataclass(frozen=True)
class SemanticQueryModelIR:
    model_module: str
    model_qualname: str
    category: str
    fields: Tuple[SemanticFieldIR, ...]


def build_semantic_model_ir(
    instance: Any,
    category: str,
    field_roles: Dict[str, str],
    state: AdapterState,
) -> SemanticQueryModelIR:
    current = object_state(instance)
    unknown = sorted(
        set(current) - set(field_roles)
    )

    if unknown:
        raise ValueError(
            "UNMAPPED_INSTANCE_FIELDS:"
            + ",".join(unknown)
        )

    semantic_fields = tuple(
        SemanticFieldIR(
            role=field_roles[name],
            source_name=name,
            value=encode_value(value, state),
        )
        for name, value in sorted(current.items())
    )

    return SemanticQueryModelIR(
        model_module=type(instance).__module__,
        model_qualname=type(instance).__qualname__,
        category=category,
        fields=semantic_fields,
    )


def lower_semantic_model_ir(
    value: SemanticQueryModelIR,
) -> PostInitModelIR:
    return PostInitModelIR(
        model_module=value.model_module,
        model_qualname=value.model_qualname,
        state=tuple(
            (
                field.source_name,
                field.value,
            )
            for field in value.fields
        ),
    )


def validate_semantic_roundtrip(
    instance: Any,
    semantic_ir: SemanticQueryModelIR,
) -> Tuple[bool, Any, Any]:
    structural_ir = lower_semantic_model_ir(
        semantic_ir
    )
    reconstructed = decode_value(structural_ir)
    original_snapshot = snapshot_value(instance)
    reconstructed_snapshot = snapshot_value(
        reconstructed
    )
    passed = (
        type(instance) is type(reconstructed)
        and original_snapshot
        == reconstructed_snapshot
    )
    return (
        passed,
        original_snapshot,
        reconstructed_snapshot,
    )
