from __future__ import annotations

import importlib
import unittest
from unittest import mock


prediction = importlib.import_module(
    "atcodertools.fmtprediction.predict_format"
)


class FakeProblemContent:
    def __init__(self, raw, context=None):
        self.raw = raw
        self.context = (
            raw
            if context is None
            else context
        )

    def get_input_format(self):
        return self.raw

    def get_input_format_blocks(self):
        return [self.raw]

    def get_input_format_context(self):
        return self.context

    def get_samples(self):
        return []


class TestTexLexicalMinimal(unittest.TestCase):
    def test_normalization_rules(self):
        cases = [
            (r"\mathit{sx}", "sx"),
            (
                r"\mathit{x+y}",
                r"\mathit{x+y}",
            ),
            (
                r"\ldotsA_",
                r"\ldots A_",
            ),
            (
                r"\vdotst_",
                r"\vdots t_",
            ),
            (
                r"\dotsb_1",
                r"\dotsb_1",
            ),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                actual = (
                    prediction
                    ._normalize_tex_recognition_text(
                        source
                    )
                )
                self.assertEqual(
                    expected,
                    actual,
                )

    def test_normalized_view(self):
        raw = (
            r"\(\mathit{sx} _ 1\)"
            "\n"
            r"A_{N,1}\ldotsA_"
            "\n"
        )
        content = FakeProblemContent(
            raw,
            r"context \mathit{gx}",
        )
        primary = (
            prediction
            ._inline_math_delimiter_content_view(
                content
            )
        )
        fallback = (
            prediction
            ._InlineMathDelimiterContentView(
                primary,
                prediction
                ._normalize_tex_recognition_text,
            )
        )

        self.assertIn(
            r"\mathit{sx}",
            primary.get_input_format(),
        )
        self.assertIn(
            "sx _ 1",
            fallback.get_input_format(),
        )
        self.assertIn(
            r"\ldots A_",
            fallback
            .get_input_format_blocks()[0],
        )
        self.assertIn(
            "gx",
            fallback
            .get_input_format_context(),
        )
        self.assertEqual(
            raw,
            content.get_input_format(),
        )

    def test_fallback_control(self):
        content = FakeProblemContent(
            r"\(\mathit{sx}\)" + "\n"
        )
        sentinel = object()

        with mock.patch.object(
            prediction,
            "_predict_format_once",
            return_value=sentinel,
        ) as predictor:
            self.assertIs(
                sentinel,
                prediction.predict_format(
                    content
                ),
            )

        self.assertEqual(
            1,
            predictor.call_count,
        )

        with mock.patch.object(
            prediction,
            "_predict_format_once",
            side_effect=[
                prediction.NoPredictionResultError,
                sentinel,
            ],
        ) as predictor:
            self.assertIs(
                sentinel,
                prediction.predict_format(
                    content
                ),
            )

        self.assertEqual(
            2,
            predictor.call_count,
        )
        self.assertIn(
            r"\mathit{sx}",
            predictor.call_args_list[0]
            .args[0]
            .get_input_format(),
        )
        self.assertEqual(
            "sx\n",
            predictor.call_args_list[1]
            .args[0]
            .get_input_format(),
        )


if __name__ == "__main__":
    unittest.main()
