from __future__ import annotations

from dataclasses import dataclass
import unittest

from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowObserver,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    QueryIRShadowValidationError,
)
from atcodertools.fmtprediction.query_ir_shadow import (
    call_with_query_ir_shadow,
)


@dataclass(frozen=True)
class ShadowFixture:
    count: str
    prefix_format: object
    fields: tuple


FIELD_ROLES = {
    "count": "COUNT_REFERENCE",
    "prefix_format": "PREFIX_FORMAT",
    "fields": "FIELDS",
}


def failing_validator(
    instance,
    semantic_ir,
):
    return (
        False,
        {
            "instance": instance,
        },
        {
            "semantic_ir": semantic_ir,
        },
    )


class QueryIRShadowObserverTest(
    unittest.TestCase,
):
    def test_observe_returns_same_object(self) -> None:
        observer = QueryIRShadowObserver()
        instance = ShadowFixture(
            count="Q",
            prefix_format=object(),
            fields=("x", "y"),
        )

        result = observer.observe(
            instance,
            "HOMOGENEOUS",
            FIELD_ROLES,
        )

        self.assertIs(result, instance)
        self.assertEqual(
            observer.observation_count,
            1,
        )
        self.assertEqual(
            observer.failure_count,
            0,
        )
        self.assertTrue(
            observer.observations[0].passed
        )

    def test_strict_failure_is_recorded(
        self,
    ) -> None:
        observer = QueryIRShadowObserver(
            validator=failing_validator,
        )
        instance = ShadowFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )

        with self.assertRaisesRegex(
            QueryIRShadowValidationError,
            "QUERY_IR_SHADOW_ROUNDTRIP_FAILED",
        ):
            observer.observe(
                instance,
                "HOMOGENEOUS",
                FIELD_ROLES,
            )

        self.assertEqual(
            observer.observation_count,
            1,
        )
        self.assertEqual(
            observer.failure_count,
            1,
        )

    def test_non_strict_failure_returns_same_object(
        self,
    ) -> None:
        observer = QueryIRShadowObserver(
            strict=False,
            validator=failing_validator,
        )
        instance = ShadowFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )

        result = observer.observe(
            instance,
            "HOMOGENEOUS",
            FIELD_ROLES,
        )

        self.assertIs(result, instance)
        self.assertEqual(
            observer.failure_count,
            1,
        )

    def test_unmapped_field_is_rejected(
        self,
    ) -> None:
        observer = QueryIRShadowObserver()
        instance = ShadowFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "UNMAPPED_INSTANCE_FIELDS:fields",
        ):
            observer.observe(
                instance,
                "HOMOGENEOUS",
                {
                    "count": "COUNT_REFERENCE",
                    "prefix_format":
                        "PREFIX_FORMAT",
                },
            )

        self.assertEqual(
            observer.observation_count,
            0,
        )

    def test_observer_states_are_isolated(
        self,
    ) -> None:
        first = QueryIRShadowObserver()
        second = QueryIRShadowObserver()
        instance = ShadowFixture(
            count="Q",
            prefix_format=object(),
            fields=(),
        )

        first.observe(
            instance,
            "HOMOGENEOUS",
            FIELD_ROLES,
        )

        self.assertEqual(
            first.observation_count,
            1,
        )
        self.assertEqual(
            second.observation_count,
            0,
        )
        self.assertIsNot(
            first.adapter_state,
            second.adapter_state,
        )

    def test_call_without_observer_forwards_arguments(
        self,
    ) -> None:
        calls = []

        def producer(left, right, scale=1):
            calls.append(
                (left, right, scale)
            )
            return {
                "value":
                    (left + right) * scale,
            }

        result = call_with_query_ir_shadow(
            producer,
            2,
            3,
            observer=None,
            category="TEST",
            field_roles={},
            scale=4,
        )

        self.assertEqual(
            result,
            {"value": 20},
        )
        self.assertEqual(
            calls,
            [(2, 3, 4)],
        )

    def test_call_with_observer_returns_same_object(
        self,
    ) -> None:
        observer = QueryIRShadowObserver()
        instance = ShadowFixture(
            count="Q",
            prefix_format=object(),
            fields=("x",),
        )

        def producer():
            return instance

        result = call_with_query_ir_shadow(
            producer,
            observer=observer,
            category="HOMOGENEOUS",
            field_roles=FIELD_ROLES,
        )

        self.assertIs(result, instance)
        self.assertEqual(
            observer.observation_count,
            1,
        )
        self.assertEqual(
            observer.failure_count,
            0,
        )

    def test_call_propagates_strict_failure(
        self,
    ) -> None:
        observer = QueryIRShadowObserver(
            validator=failing_validator,
        )
        instance = ShadowFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )

        with self.assertRaisesRegex(
            QueryIRShadowValidationError,
            "QUERY_IR_SHADOW_ROUNDTRIP_FAILED",
        ):
            call_with_query_ir_shadow(
                lambda: instance,
                observer=observer,
                category="HOMOGENEOUS",
                field_roles=FIELD_ROLES,
            )

        self.assertEqual(
            observer.failure_count,
            1,
        )

    def test_call_rejects_observer_identity_change(
        self,
    ) -> None:
        instance = ShadowFixture(
            count="Q",
            prefix_format=None,
            fields=(),
        )

        class ReplacingObserver:
            def observe(
                self,
                instance,
                category,
                field_roles,
            ):
                return object()

        with self.assertRaisesRegex(
            QueryIRShadowValidationError,
            "QUERY_IR_SHADOW_RESULT_IDENTITY_CHANGED",
        ):
            call_with_query_ir_shadow(
                lambda: instance,
                observer=ReplacingObserver(),
                category="HOMOGENEOUS",
                field_roles=FIELD_ROLES,
            )


if __name__ == "__main__":
    unittest.main()
