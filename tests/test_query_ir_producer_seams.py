from __future__ import annotations

from dataclasses import dataclass
import unittest
from unittest.mock import patch

from atcodertools.fmtprediction import (
    query_ir_producer_seams,
)
from atcodertools.fmtprediction.query_ir_producer_seams import (
    _create_prediction_with_shadow,
)
from atcodertools.fmtprediction.query_ir_producer_seams import (
    _create_tagged_query_typed_format_with_shadow,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowObserver,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowValidationError,
)


@dataclass(frozen=True)
class ProducerSeamFixture:
    count: str
    prefix_format: object
    fields: tuple


FIXTURE_KEY = (
    ProducerSeamFixture.__module__,
    ProducerSeamFixture.__qualname__,
)

FIXTURE_SPECS = {
    FIXTURE_KEY: (
        "HOMOGENEOUS",
        {
            "count": "COUNT_REFERENCE",
            "prefix_format": "PREFIX_FORMAT",
            "fields": "FIELDS",
        },
    ),
}


class QueryIRProducerSeamsTest(
    unittest.TestCase,
):
    def test_tagged_format_without_observer_forwards(
        self,
    ) -> None:
        calls = []
        result = object()

        def producer(format_, var_to_type):
            calls.append((format_, var_to_type))
            return result

        with patch.object(
            query_ir_producer_seams,
            "_CREATE_TAGGED_QUERY_TYPED_FORMAT",
            producer,
            create=True,
        ):
            returned = (
                _create_tagged_query_typed_format_with_shadow(
                    producer,
                    "format",
                    {"Q": int},
                )
            )

        self.assertIs(returned, result)
        self.assertEqual(
            calls,
            [("format", {"Q": int})],
        )

    def test_tagged_format_observes_nested_target(
        self,
    ) -> None:
        fixture = ProducerSeamFixture(
            count="Q",
            prefix_format=object(),
            fields=("x",),
        )
        result = {"fixture": fixture}
        observer = QueryIRShadowObserver()

        with patch.object(
            query_ir_producer_seams,
            "_CREATE_TAGGED_QUERY_TYPED_FORMAT",
            lambda format_, var_to_type: result,
            create=True,
        ), patch.object(
            query_ir_producer_seams,
            "_PR324_TARGET_SPECS",
            FIXTURE_SPECS,
        ):
            returned = (
                _create_tagged_query_typed_format_with_shadow(
                    query_ir_producer_seams._CREATE_TAGGED_QUERY_TYPED_FORMAT,
                    "format",
                    {},
                    observer=observer,
                )
            )

        self.assertIs(returned, result)
        self.assertEqual(observer.observation_count, 1)
        self.assertEqual(observer.failure_count, 0)

    def test_prediction_wrapper_forwards_and_observes(
        self,
    ) -> None:
        fixture = ProducerSeamFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )
        result = [fixture]
        calls = []
        observer = QueryIRShadowObserver()

        def producer(
            prefix_format,
            query_count_var,
            definitions,
            samples,
        ):
            calls.append(
                (
                    prefix_format,
                    query_count_var,
                    definitions,
                    samples,
                )
            )
            return result

        with patch.object(
            query_ir_producer_seams,
            "_CREATE_PREDICTION",
            producer,
            create=True,
        ), patch.object(
            query_ir_producer_seams,
            "_PR324_TARGET_SPECS",
            FIXTURE_SPECS,
        ):
            returned = _create_prediction_with_shadow(
                producer,
                "prefix",
                "Q",
                ("definition",),
                ("sample",),
                observer=observer,
            )

        self.assertIs(returned, result)
        self.assertEqual(
            calls,
            [
                (
                    "prefix",
                    "Q",
                    ("definition",),
                    ("sample",),
                )
            ],
        )
        self.assertEqual(observer.observation_count, 1)

    def test_observer_rejects_missing_target(
        self,
    ) -> None:
        observer = QueryIRShadowObserver()

        with patch.object(
            query_ir_producer_seams,
            "_CREATE_PREDICTION",
            lambda *args: object(),
            create=True,
        ), patch.object(
            query_ir_producer_seams,
            "_PR324_TARGET_SPECS",
            FIXTURE_SPECS,
        ):
            with self.assertRaisesRegex(
                QueryIRShadowValidationError,
                "QUERY_IR_SHADOW_TARGET_NOT_REACHABLE",
            ):
                _create_prediction_with_shadow(
                    query_ir_producer_seams._CREATE_PREDICTION,
                    None,
                    "Q",
                    (),
                    (),
                    observer=observer,
                )

    def test_pr324_target_specs_are_complete(
        self,
    ) -> None:
        class_names = {
            class_name
            for _, class_name in (
                query_ir_producer_seams
                ._PR324_TARGET_SPECS
            )
        }

        self.assertEqual(
            class_names,
            {
                "TaggedQueryArgument",
                "TaggedQueryFormat",
                "TaggedQueryPrediction",
                "TaggedQueryVariant",
            },
        )

    def test_homogeneous_format_forwards_and_observes(
        self,
    ) -> None:
        fixture = ProducerSeamFixture(
            count="Q",
            prefix_format=object(),
            fields=("x",),
        )
        result = {
            "fixture": fixture,
        }
        calls = []
        observer = QueryIRShadowObserver()

        def producer(
            format_,
            var_to_type,
        ):
            calls.append(
                (
                    format_,
                    var_to_type,
                )
            )
            return result

        with patch.object(
            query_ir_producer_seams,
            "_PR325_HOMOGENEOUS_TARGET_SPECS",
            FIXTURE_SPECS,
        ):
            returned = (
                query_ir_producer_seams
                ._create_homogeneous_query_typed_format_with_shadow(
                    producer,
                    "format",
                    {"Q": int},
                    observer=observer,
                )
            )

        self.assertIs(returned, result)
        self.assertEqual(
            calls,
            [
                (
                    "format",
                    {"Q": int},
                )
            ],
        )
        self.assertEqual(
            observer.observation_count,
            1,
        )

    def test_homogeneous_prediction_forwards_and_observes(
        self,
    ) -> None:
        fixture = ProducerSeamFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )
        result = [fixture]
        calls = []
        observer = QueryIRShadowObserver()

        def producer(
            prefix_format,
            query_count_var,
            argument_names,
            samples,
        ):
            calls.append(
                (
                    prefix_format,
                    query_count_var,
                    argument_names,
                    samples,
                )
            )
            return result

        with patch.object(
            query_ir_producer_seams,
            "_PR325_HOMOGENEOUS_TARGET_SPECS",
            FIXTURE_SPECS,
        ):
            returned = (
                query_ir_producer_seams
                ._create_homogeneous_prediction_with_shadow(
                    producer,
                    "prefix",
                    "Q",
                    ("x",),
                    ("sample",),
                    observer=observer,
                )
            )

        self.assertIs(returned, result)
        self.assertEqual(
            calls,
            [
                (
                    "prefix",
                    "Q",
                    ("x",),
                    ("sample",),
                )
            ],
        )
        self.assertEqual(
            observer.observation_count,
            1,
        )

    def test_pr325_homogeneous_specs_are_complete(
        self,
    ) -> None:
        class_names = {
            class_name
            for _, class_name
            in (
                query_ir_producer_seams
                ._PR325_HOMOGENEOUS_TARGET_SPECS
            )
        }

        self.assertEqual(
            class_names,
            {
                "HomogeneousQueryFormat",
                "HomogeneousQueryPrediction",
                "TaggedQueryArgument",
            },
        )


if __name__ == "__main__":
    unittest.main()
