import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.models.ragged_format import (
    RaggedRowFormat,
)
from atcodertools.fmtprediction.predict_format import (
    NoPredictionResultError,
    predict_format,
)


def same_line_with_suffix_content():
    return ProblemContent(
        input_format_text=(
            "N Q\n"
            "L_1 a_{1,1} "
            "... a_{1,L_1}\n"
            "...\n"
            "L_N a_{N,1} "
            "... a_{N,L_N}\n"
            "s_1 t_1\n"
            "...\n"
            "s_Q t_Q\n"
        ),
        samples=[
            Sample(
                (
                    "2 2\n"
                    "2 10 20\n"
                    "1 30\n"
                    "1 1\n"
                    "2 1\n"
                ),
                "",
            ),
        ],
    )


def rectangular_content():
    return ProblemContent(
        input_format_text=(
            "N\n"
            "A_1 ... A_N\n"
        ),
        samples=[
            Sample(
                "3\n1 2 3\n",
                "",
            ),
        ],
    )


def two_line_content():
    return ProblemContent(
        input_format_text=(
            "N K\n"
            "d_1\n"
            "A_{1,1} ... A_{1,d_1}\n"
            "...\n"
            "d_K\n"
            "A_{K,1} ... A_{K,d_K}\n"
        ),
        samples=[
            Sample(
                (
                    "4 3\n"
                    "2\n"
                    "1 2\n"
                    "1\n"
                    "3\n"
                    "2\n"
                    "2 4\n"
                ),
                "",
            ),
        ],
    )


class TestRaggedRowPredictFormatBridge(
    unittest.TestCase
):
    def test_same_line_ragged_uses_fallback(
        self,
    ):
        result = predict_format(
            same_line_with_suffix_content()
        )

        self.assertIsInstance(
            result.format,
            RaggedRowFormat,
        )

        self.assertEqual(
            [
                "N",
                "Q",
                "L",
                "a",
                "s",
                "t",
            ],
            [
                variable.name
                for variable
                in result.format.all_vars()
            ],
        )

        self.assertEqual(
            "[(Parallel: s,t | 1 to Q)]",
            str(
                result.format.suffix_format
            ),
        )

    def test_ordinary_rectangular_format_is_unchanged(
        self,
    ):
        result = predict_format(
            rectangular_content()
        )

        self.assertNotIsInstance(
            result.format,
            RaggedRowFormat,
        )

    def test_two_line_ragged_remains_followup(
        self,
    ):
        with self.assertRaises(
            NoPredictionResultError
        ):
            predict_format(
                two_line_content()
            )


if __name__ == "__main__":
    unittest.main()
