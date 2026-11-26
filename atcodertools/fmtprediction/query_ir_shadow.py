from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple

from atcodertools.fmtprediction.query_ir import (
    SemanticQueryModelIR,
)
from atcodertools.fmtprediction.query_ir import (
    build_semantic_model_ir,
)
from atcodertools.fmtprediction.query_ir import (
    validate_semantic_roundtrip,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    AdapterState,
)


RoundtripValidator = Callable[
    [
        Any,
        SemanticQueryModelIR,
    ],
    Tuple[
        bool,
        Any,
        Any,
    ],
]


class QueryIRShadowValidationError(
    RuntimeError,
):
    pass


@dataclass(frozen=True)
class ShadowObservation:
    category: str
    model_module: str
    model_qualname: str
    semantic_ir: SemanticQueryModelIR
    passed: bool
    original_snapshot: Any
    reconstructed_snapshot: Any


class QueryIRShadowObserver:
    def __init__(
        self,
        strict: bool = True,
        validator: Optional[
            RoundtripValidator
        ] = None,
    ) -> None:
        self._strict = strict
        self._validator = (
            validator
            if validator is not None
            else validate_semantic_roundtrip
        )
        self._state = AdapterState()
        self._observations: list[
            ShadowObservation
        ] = []

    @property
    def observations(
        self,
    ) -> Tuple[ShadowObservation, ...]:
        return tuple(self._observations)

    @property
    def observation_count(self) -> int:
        return len(self._observations)

    @property
    def failure_count(self) -> int:
        return sum(
            not observation.passed
            for observation
            in self._observations
        )

    @property
    def adapter_state(self) -> AdapterState:
        return self._state

    def observe(
        self,
        instance: Any,
        category: str,
        field_roles: Dict[str, str],
    ) -> Any:
        semantic_ir = build_semantic_model_ir(
            instance=instance,
            category=category,
            field_roles=field_roles,
            state=self._state,
        )

        (
            passed,
            original_snapshot,
            reconstructed_snapshot,
        ) = self._validator(
            instance,
            semantic_ir,
        )

        observation = ShadowObservation(
            category=category,
            model_module=type(instance).__module__,
            model_qualname=type(
                instance
            ).__qualname__,
            semantic_ir=semantic_ir,
            passed=passed,
            original_snapshot=original_snapshot,
            reconstructed_snapshot=(
                reconstructed_snapshot
            ),
        )
        self._observations.append(
            observation
        )

        if not passed and self._strict:
            raise QueryIRShadowValidationError(
                "QUERY_IR_SHADOW_ROUNDTRIP_FAILED:"
                + type(instance).__module__
                + "."
                + type(instance).__qualname__
            )

        return instance


def call_with_query_ir_shadow(
    producer: Callable[..., Any],
    *args: Any,
    observer: Optional[
        QueryIRShadowObserver
    ] = None,
    category: str,
    field_roles: Dict[str, str],
    **kwargs: Any,
) -> Any:
    result = producer(*args, **kwargs)

    if observer is None:
        return result

    observed = observer.observe(
        instance=result,
        category=category,
        field_roles=field_roles,
    )

    if observed is not result:
        raise QueryIRShadowValidationError(
            "QUERY_IR_SHADOW_RESULT_IDENTITY_CHANGED"
        )

    return result
