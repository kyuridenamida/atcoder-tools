from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from enum import Enum
import importlib
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union


@dataclass(frozen=True)
class SequenceIR:
    kind: str
    values: Tuple[Any, ...]


@dataclass(frozen=True)
class MappingIR:
    entries: Tuple[Tuple[Any, Any], ...]


@dataclass(frozen=True)
class EnumIR:
    module: str
    qualname: str
    name: str


@dataclass(frozen=True)
class TypeIR:
    module: str
    qualname: str


@dataclass(frozen=True)
class ExternalLeafIR:
    type_module: str
    type_qualname: str
    value: Any


@dataclass(frozen=True)
class ConstructorModelIR:
    model_module: str
    model_qualname: str
    positional: Tuple[Any, ...]
    keywords: Tuple[Tuple[str, Any], ...]


@dataclass(frozen=True)
class PostInitModelIR:
    model_module: str
    model_qualname: str
    state: Tuple[Tuple[str, Any], ...]


QueryModelIR = Union[
    ConstructorModelIR,
    PostInitModelIR,
]


class AdapterState:
    def __init__(self) -> None:
        self._remembered: Dict[
            int,
            Tuple[Any, QueryModelIR],
        ] = {}
        self.identity_hit_count = 0
        self.identity_miss_count = 0
        self.stale_id_rejection_count = 0
        self.external_leaf_types: Dict[str, int] = {}

    @property
    def remembered_object_count(self) -> int:
        return len(self._remembered)

    def remember(
        self,
        instance: Any,
        model_ir: QueryModelIR,
    ) -> None:
        self._remembered[id(instance)] = (
            instance,
            model_ir,
        )

    def find(
        self,
        value: Any,
    ) -> Optional[QueryModelIR]:
        entry = self._remembered.get(id(value))

        if entry is None:
            self.identity_miss_count += 1
            return None

        remembered_instance, remembered_ir = entry

        if remembered_instance is value:
            self.identity_hit_count += 1
            return remembered_ir

        self.stale_id_rejection_count += 1
        del self._remembered[id(value)]
        return None

    def external_leaf(
        self,
        value: Any,
    ) -> ExternalLeafIR:
        value_type = type(value)
        key = (
            value_type.__module__
            + "."
            + value_type.__qualname__
        )
        self.external_leaf_types[key] = (
            self.external_leaf_types.get(key, 0)
            + 1
        )
        return ExternalLeafIR(
            type_module=value_type.__module__,
            type_qualname=value_type.__qualname__,
            value=value,
        )


def _resolve_qualname(
    module_name: str,
    qualname: str,
) -> Any:
    value = importlib.import_module(module_name)

    for part in qualname.split("."):
        value = getattr(value, part)

    return value


def encode_value(
    value: Any,
    state: AdapterState,
) -> Any:
    remembered = state.find(value)

    if remembered is not None:
        return remembered

    if value is None or isinstance(
        value,
        (bool, int, float, str, bytes),
    ):
        return value

    if isinstance(value, Enum):
        return EnumIR(
            module=type(value).__module__,
            qualname=type(value).__qualname__,
            name=value.name,
        )

    if isinstance(value, type):
        return TypeIR(
            module=value.__module__,
            qualname=value.__qualname__,
        )

    if isinstance(value, tuple):
        return SequenceIR(
            kind="tuple",
            values=tuple(
                encode_value(item, state)
                for item in value
            ),
        )

    if isinstance(value, list):
        return SequenceIR(
            kind="list",
            values=tuple(
                encode_value(item, state)
                for item in value
            ),
        )

    if isinstance(value, set):
        encoded = [
            encode_value(item, state)
            for item in value
        ]
        encoded.sort(key=repr)
        return SequenceIR(
            kind="set",
            values=tuple(encoded),
        )

    if isinstance(value, frozenset):
        encoded = [
            encode_value(item, state)
            for item in value
        ]
        encoded.sort(key=repr)
        return SequenceIR(
            kind="frozenset",
            values=tuple(encoded),
        )

    if isinstance(value, dict):
        entries = [
            (
                encode_value(key, state),
                encode_value(current, state),
            )
            for key, current in value.items()
        ]
        entries.sort(key=repr)
        return MappingIR(entries=tuple(entries))

    return state.external_leaf(value)


def decode_value(value: Any) -> Any:
    if isinstance(value, ConstructorModelIR):
        model_class = _resolve_qualname(
            value.model_module,
            value.model_qualname,
        )
        positional = tuple(
            decode_value(item)
            for item in value.positional
        )
        keywords = {
            key: decode_value(current)
            for key, current in value.keywords
        }
        return model_class(*positional, **keywords)

    if isinstance(value, PostInitModelIR):
        model_class = _resolve_qualname(
            value.model_module,
            value.model_qualname,
        )
        instance = model_class.__new__(model_class)

        for name, encoded in value.state:
            object.__setattr__(
                instance,
                name,
                decode_value(encoded),
            )

        return instance

    if isinstance(value, SequenceIR):
        decoded = [
            decode_value(item)
            for item in value.values
        ]
        constructors = {
            "tuple": tuple,
            "list": list,
            "set": set,
            "frozenset": frozenset,
        }
        return constructors[value.kind](decoded)

    if isinstance(value, MappingIR):
        return {
            decode_value(key): decode_value(current)
            for key, current in value.entries
        }

    if isinstance(value, EnumIR):
        enum_class = _resolve_qualname(
            value.module,
            value.qualname,
        )
        return enum_class[value.name]

    if isinstance(value, TypeIR):
        return _resolve_qualname(
            value.module,
            value.qualname,
        )

    if isinstance(value, ExternalLeafIR):
        return value.value

    return value


def object_state(instance: Any) -> Dict[str, Any]:
    state: Dict[str, Any] = {}

    if is_dataclass(instance):
        for field in fields(instance):
            state[field.name] = getattr(
                instance,
                field.name,
            )
        return state

    if hasattr(instance, "__dict__"):
        state.update(vars(instance))

    slots: Iterable[str] = getattr(
        type(instance),
        "__slots__",
        (),
    )

    if isinstance(slots, str):
        slots = (slots,)

    for name in slots:
        if (
            name not in state
            and hasattr(instance, name)
        ):
            state[name] = getattr(instance, name)

    return state


def make_post_init_model_ir(
    instance: Any,
    state: AdapterState,
) -> PostInitModelIR:
    current = object_state(instance)
    encoded = tuple(
        sorted(
            (
                name,
                encode_value(value, state),
            )
            for name, value in current.items()
        )
    )
    return PostInitModelIR(
        model_module=type(instance).__module__,
        model_qualname=type(instance).__qualname__,
        state=encoded,
    )


def snapshot_value(
    value: Any,
    seen: Optional[set] = None,
) -> Any:
    if seen is None:
        seen = set()

    if value is None or isinstance(
        value,
        (bool, int, float, str, bytes),
    ):
        return value

    if isinstance(value, Enum):
        return {
            "enum_type": (
                type(value).__module__
                + "."
                + type(value).__qualname__
            ),
            "name": value.name,
        }

    if isinstance(value, type):
        return {
            "type": (
                value.__module__
                + "."
                + value.__qualname__
            ),
        }

    value_id = id(value)

    if value_id in seen:
        return {
            "cycle": (
                type(value).__module__
                + "."
                + type(value).__qualname__
            ),
        }

    seen.add(value_id)

    try:
        if isinstance(value, tuple):
            return {
                "tuple": [
                    snapshot_value(item, seen)
                    for item in value
                ],
            }

        if isinstance(value, list):
            return {
                "list": [
                    snapshot_value(item, seen)
                    for item in value
                ],
            }

        if isinstance(value, (set, frozenset)):
            items = [
                snapshot_value(item, seen)
                for item in value
            ]
            items.sort(key=repr)
            return {
                type(value).__name__: items,
            }

        if isinstance(value, dict):
            items = [
                (
                    snapshot_value(key, seen),
                    snapshot_value(current, seen),
                )
                for key, current in value.items()
            ]
            items.sort(key=repr)
            return {"dict": items}

        current = object_state(value)

        if current:
            key = (
                "fields"
                if is_dataclass(value)
                else "state"
            )
            return {
                "model_type": (
                    type(value).__module__
                    + "."
                    + type(value).__qualname__
                ),
                key: {
                    name: snapshot_value(
                        current_value,
                        seen,
                    )
                    for name, current_value
                    in sorted(current.items())
                },
            }

        return {
            "opaque_type": (
                type(value).__module__
                + "."
                + type(value).__qualname__
            ),
            "repr": repr(value),
        }

    finally:
        seen.remove(value_id)


def validate_roundtrip(
    instance: Any,
    model_ir: QueryModelIR,
) -> Tuple[bool, Any, Any]:
    reconstructed = decode_value(model_ir)
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
