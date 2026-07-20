from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
