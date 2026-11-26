from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import unittest

from atcodertools.fmtprediction.query_ir_lowering import (
    AdapterState,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    decode_value,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    encode_value,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    make_post_init_model_ir,
)
from atcodertools.fmtprediction.query_ir_lowering import (
    validate_roundtrip,
)


class SampleKind(Enum):
    FIRST = 1
    SECOND = 2


@dataclass(frozen=True)
class ChildModel:
    name: str
    kind: SampleKind


@dataclass(frozen=True)
class ParentModel:
    child: ChildModel
    values: tuple


class ExternalValue:
    pass


class QueryIRLoweringTest(unittest.TestCase):
    def test_post_init_roundtrip(self) -> None:
        state = AdapterState()
        instance = ChildModel(
            name="x",
            kind=SampleKind.SECOND,
        )
        model_ir = make_post_init_model_ir(
            instance,
            state,
        )
        passed, original, reconstructed = (
            validate_roundtrip(
                instance,
                model_ir,
            )
        )
        self.assertTrue(passed)
        self.assertEqual(original, reconstructed)

    def test_nested_remembered_ir_uses_identity(self) -> None:
        state = AdapterState()
        child = ChildModel(
            name="nested",
            kind=SampleKind.FIRST,
        )
        child_ir = make_post_init_model_ir(
            child,
            state,
        )
        state.remember(child, child_ir)

        parent = ParentModel(
            child=child,
            values=(1, 2, 3),
        )
        parent_ir = make_post_init_model_ir(
            parent,
            state,
        )
        passed, original, reconstructed = (
            validate_roundtrip(
                parent,
                parent_ir,
            )
        )
        self.assertTrue(passed)
        self.assertEqual(original, reconstructed)
        self.assertGreaterEqual(
            state.identity_hit_count,
            1,
        )

    def test_external_leaf_is_preserved(self) -> None:
        state = AdapterState()
        value = ExternalValue()
        encoded = encode_value(value, state)
        decoded = decode_value(encoded)
        self.assertIs(decoded, value)
        self.assertEqual(
            sum(state.external_leaf_types.values()),
            1,
        )

    def test_states_are_isolated(self) -> None:
        first = AdapterState()
        second = AdapterState()
        value = ExternalValue()
        encode_value(value, first)
        self.assertEqual(
            first.remembered_object_count,
            0,
        )
        self.assertEqual(
            second.external_leaf_types,
            {},
        )


if __name__ == "__main__":
    unittest.main()
