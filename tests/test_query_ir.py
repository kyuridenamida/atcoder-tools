from __future__ import annotations

from dataclasses import dataclass
import unittest

from atcodertools.fmtprediction.query_ir import (
    HomogeneousQuerySpec,
)
from atcodertools.fmtprediction.query_ir import (
    QueryFieldSpec,
)
from atcodertools.fmtprediction.query_ir import (
    QueryInputSpec,
)
from atcodertools.fmtprediction.query_ir import (
    ScalarReference,
)
from atcodertools.fmtprediction.query_ir import (
    TaggedQuerySpec,
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


@dataclass(frozen=True)
class SemanticFixture:
    count: str
    prefix_format: object
    fields: tuple


class QueryIRTest(unittest.TestCase):
    def test_semantic_model_roundtrip(self) -> None:
        state = AdapterState()
        prefix = object()
        instance = SemanticFixture(
            count="Q",
            prefix_format=prefix,
            fields=("x", "y"),
        )
        roles = {
            "count": "COUNT_REFERENCE",
            "prefix_format": "PREFIX_FORMAT",
            "fields": "FIELDS",
        }
        semantic_ir = build_semantic_model_ir(
            instance,
            "HOMOGENEOUS",
            roles,
            state,
        )
        passed, original, reconstructed = (
            validate_semantic_roundtrip(
                instance,
                semantic_ir,
            )
        )
        self.assertTrue(passed)
        self.assertEqual(original, reconstructed)

    def test_unmapped_field_is_rejected(self) -> None:
        state = AdapterState()
        instance = SemanticFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )
        with self.assertRaisesRegex(
            ValueError,
            "UNMAPPED_INSTANCE_FIELDS:fields",
        ):
            build_semantic_model_ir(
                instance,
                "HOMOGENEOUS",
                {
                    "count": "COUNT_REFERENCE",
                    "prefix_format":
                        "PREFIX_FORMAT",
                },
                state,
            )

    def test_canonical_query_input_specs(self) -> None:
        count = ScalarReference(name="Q")
        field = QueryFieldSpec(
            name="x",
            value_type=int,
        )
        homogeneous = HomogeneousQuerySpec(
            prefix_format=None,
            count=count,
            fields=(field,),
        )
        tagged = TaggedQuerySpec(
            prefix_format=None,
            count=count,
            variants=(),
        )
        self.assertEqual(
            QueryInputSpec(
                body=homogeneous
            ).body.count,
            count,
        )
        self.assertEqual(
            QueryInputSpec(
                body=tagged
            ).body.count,
            count,
        )


if __name__ == "__main__":
    unittest.main()
