from __future__ import annotations

import importlib

import unittest
from unittest import mock

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.predict_format import (
    _inline_math_delimiter_content_view,
    _normalize_layout_tex_commands,
    predict_format,
)


predict_format_module = importlib.import_module(
    "atcodertools.fmtprediction.predict_format"
)


class FakeProblemContent:
    def __init__(
        self,
        input_format,
        blocks,
        context,
    ):
        self._input_format = input_format
        self._blocks = list(blocks)
        self._context = context

    def get_input_format(self):
        return self._input_format

    def get_input_format_blocks(self):
        return list(self._blocks)

    def get_input_format_context(self):
        return self._context


class TestInlineMathDelimiterNormalization(
    unittest.TestCase
):
    def test_removes_inline_math_delimiters(self):
        source = (
            "\\(N\\)\n"
            "\\(A_1\\) \\(A_2\\) "
            "\\(\\ldots\\) \\(A_N\\)\n"
        )

        normalized = (
            _normalize_layout_tex_commands(
                source
            )
        )

        self.assertNotIn(
            "\\(",
            normalized,
        )
        self.assertNotIn(
            "\\)",
            normalized,
        )
        self.assertIn(
            "A_1",
            normalized,
        )

    def test_preserves_ordinary_parentheses(self):
        source = (
            "N\n"
            "A_{(N-1)}\n"
        )

        normalized = (
            _normalize_layout_tex_commands(
                source
            )
        )

        self.assertIn(
            "A_{(N-1)}",
            normalized,
        )

    def test_content_view_normalizes_all_representations(self):
        raw = (
            "\\(N\\)\n"
            "\\(A_1\\) \\(A_N\\)\n"
        )

        content = FakeProblemContent(
            raw,
            [raw],
            "context \\(N\\)",
        )

        view = (
            _inline_math_delimiter_content_view(
                content
            )
        )

        self.assertNotIn(
            "\\(",
            view.get_input_format(),
        )
        self.assertNotIn(
            "\\(",
            view.get_input_format_blocks()[0],
        )
        self.assertNotIn(
            "\\(",
            view.get_input_format_context(),
        )

        self.assertEqual(
            raw,
            content.get_input_format(),
        )
        self.assertEqual(
            [raw],
            content.get_input_format_blocks(),
        )
        self.assertEqual(
            "context \\(N\\)",
            content.get_input_format_context(),
        )

    def test_end_to_end_simple_array(self):
        content = ProblemContent(
            input_format_text=(
                "\\(N\\)\n"
                "\\(A_1\\) \\(A_2\\) "
                "\\(\\ldots\\) \\(A_N\\)\n"
            ),
            samples=[
                Sample(
                    "3\n1 2 3\n",
                    "",
                ),
            ],
        )

        prediction = predict_format(
            content
        )

        self.assertEqual(
            (
                "[(Singular: N),"
                "(Parallel: A | 1 to N)]"
            ),
            str(prediction.format),
        )

    def test_unwraps_simple_mathit_identifiers(self):
        source = (
            "N\n"
            r"\mathit{sx} _ 1 "
            r"\mathit{sy} _ 1"
            "\n"
        )

        normalized = (
            predict_format_module
            ._normalize_tex_recognition_text(
                source
            )
        )

        self.assertIn(
            "sx _ 1 sy _ 1",
            normalized,
        )
        self.assertNotIn(
            r"\mathit",
            normalized,
        )

    def test_preserves_non_identifier_mathit_expression(self):
        source = (
            r"\mathit{x+y}"
            "\n"
        )

        normalized = (
            predict_format_module
            ._normalize_tex_recognition_text(
                source
            )
        )

        self.assertIn(
            r"\mathit{x+y}",
            normalized,
        )

    def test_restores_layout_command_identifier_boundary(self):
        source = (
            "N\n"
            r"A_{N,1}\ldotsA_{N,N-1}"
            "\n"
            r"\vdotst_1"
            "\n"
        )

        normalized = (
            predict_format_module
            ._normalize_tex_recognition_text(
                source
            )
        )

        self.assertIn(
            r"\ldots A_{N,N-1}",
            normalized,
        )
        self.assertIn(
            r"\vdots t_1",
            normalized,
        )

    def test_preserves_dots_family_command_names(self):
        source = (
            r"\dotsb_1 "
            r"\dotsc_1 "
            r"\dotsi_1 "
            r"\dotsm_1 "
            r"\dotso_1"
            "\n"
        )

        normalized = (
            predict_format_module
            ._normalize_tex_recognition_text(
                source
            )
        )

        self.assertEqual(
            source,
            normalized,
        )

    def test_fallback_content_view_applies_tex_lexical_normalization(
        self,
    ):
        raw = (
            r"\(\mathit{sx} _ 1\)"
            "\n"
            r"A_{N,1}\ldotsA_{N,N-1}"
            "\n"
        )

        content = FakeProblemContent(
            raw,
            [raw],
            "context "
            + r"\mathit{gx}",
        )

        primary_view = (
            _inline_math_delimiter_content_view(
                content
            )
        )

        fallback_view = (
            predict_format_module
            ._tex_lexical_normalization_content_view(
                primary_view
            )
        )

        self.assertIn(
            "sx _ 1",
            fallback_view.get_input_format(),
        )
        self.assertIn(
            r"\ldots A_",
            fallback_view
            .get_input_format_blocks()[0],
        )
        self.assertIn(
            "gx",
            fallback_view
            .get_input_format_context(),
        )

        self.assertIn(
            r"\mathit{sx}",
            primary_view.get_input_format(),
        )
        self.assertIn(
            r"\ldotsA_",
            primary_view
            .get_input_format_blocks()[0],
        )

        self.assertEqual(
            raw,
            content.get_input_format(),
        )
        self.assertEqual(
            [raw],
            content.get_input_format_blocks(),
        )

    def test_successful_primary_prediction_skips_lexical_fallback(
        self,
    ):
        sentinel = object()

        content = FakeProblemContent(
            r"\(\mathit{sx}\)" + "\n",
            [r"\(\mathit{sx}\)" + "\n"],
            r"\(\mathit{sx}\)",
        )

        with mock.patch.object(
            predict_format_module,
            "_predict_format_from_content",
            return_value=sentinel,
        ) as predictor:
            result = (
                predict_format_module
                .predict_format(content)
            )

        self.assertIs(
            sentinel,
            result,
        )
        self.assertEqual(
            1,
            predictor.call_count,
        )

        primary_content = (
            predictor.call_args.args[0]
        )

        self.assertIn(
            r"\mathit{sx}",
            primary_content.get_input_format(),
        )
        self.assertNotIn(
            r"\(",
            primary_content.get_input_format(),
        )

    def test_lexical_fallback_runs_only_after_no_result(
        self,
    ):
        sentinel = object()

        content = FakeProblemContent(
            r"\(\mathit{sx}\)" + "\n",
            [r"\(\mathit{sx}\)" + "\n"],
            r"\(\mathit{sx}\)",
        )

        with mock.patch.object(
            predict_format_module,
            "_predict_format_from_content",
            side_effect=[
                predict_format_module
                .NoPredictionResultError,
                sentinel,
            ],
        ) as predictor:
            result = (
                predict_format_module
                .predict_format(content)
            )

        self.assertIs(
            sentinel,
            result,
        )
        self.assertEqual(
            2,
            predictor.call_count,
        )

        primary_content = (
            predictor.call_args_list[0]
            .args[0]
        )

        fallback_content = (
            predictor.call_args_list[1]
            .args[0]
        )

        self.assertIn(
            r"\mathit{sx}",
            primary_content.get_input_format(),
        )
        self.assertEqual(
            "sx\n",
            fallback_content.get_input_format(),
        )

    def test_primary_layout_normalizer_preserves_fallback_tokens(
        self,
    ):
        source = (
            r"\mathit{sx}"
            "\n"
            r"A_{N,1}\ldotsA_{N,N-1}"
            "\n"
        )

        normalized = (
            _normalize_layout_tex_commands(
                source
            )
        )

        self.assertIn(
            r"\mathit{sx}",
            normalized,
        )
        self.assertIn(
            r"\ldotsA_",
            normalized,
        )


if __name__ == "__main__":
    unittest.main()
