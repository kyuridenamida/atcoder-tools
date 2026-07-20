import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.two_line_ragged_row import (
    NoTwoLineRaggedRowPredictionError,
    detect_two_line_ragged_row_schemas,
    predict_two_line_ragged_rows,
)


def make_content(value_lines):
    return ProblemContent(
        input_format_text=(
            "N\n"
            "C_1\n"
            + value_lines[0]
            + "\n"
            "\\vdots\n"
            "C_N\n"
            + value_lines[1]
            + "\n"
            "X\n"
        ),
        samples=[
            Sample(
                (
                    "2\n"
                    "3\n"
                    "10 20 30\n"
                    "2\n"
                    "40 50\n"
                    "7\n"
                ),
                "",
            ),
        ],
    )


class TestTwoLineRaggedExplicitPrefix(
    unittest.TestCase
):
    def test_accepts_consecutive_explicit_prefix(
        self,
    ):
        content = make_content(
            (
                (
                    "A_{1,1} A_{1,2} "
                    "\\ldots A_{1,C_1}"
                ),
                (
                    "A_{N,1} A_{N,2} "
                    "\\ldots A_{N,C_N}"
                ),
            )
        )

        prediction = (
            predict_two_line_ragged_rows(
                content
            )
        )

        self.assertEqual(
            "N",
            prediction.schema.row_count_var,
        )
        self.assertEqual(
            ("C",),
            prediction.schema.prefix_fields,
        )
        self.assertEqual(
            "A",
            prediction.schema.values_name,
        )
        self.assertEqual(
            1,
            prediction.schema.value_start_index,
        )
        self.assertEqual(
            ["X"],
            [
                variable.name
                for variable
                in prediction.suffix_format.all_vars()
            ],
        )

    def test_rejects_nonconsecutive_prefix(
        self,
    ):
        content = make_content(
            (
                (
                    "A_{1,1} A_{1,3} "
                    "\\ldots A_{1,C_1}"
                ),
                (
                    "A_{N,1} A_{N,3} "
                    "\\ldots A_{N,C_N}"
                ),
            )
        )

        self.assertEqual(
            [],
            detect_two_line_ragged_row_schemas(
                content
            ),
        )

        with self.assertRaises(
            NoTwoLineRaggedRowPredictionError
        ):
            predict_two_line_ragged_rows(
                content
            )

    def test_rejects_prefix_starting_at_two(
        self,
    ):
        content = make_content(
            (
                (
                    "A_{1,2} "
                    "\\ldots A_{1,C_1}"
                ),
                (
                    "A_{N,2} "
                    "\\ldots A_{N,C_N}"
                ),
            )
        )

        self.assertEqual(
            [],
            detect_two_line_ragged_row_schemas(
                content
            ),
        )

        with self.assertRaises(
            NoTwoLineRaggedRowPredictionError
        ):
            predict_two_line_ragged_rows(
                content
            )


if __name__ == "__main__":
    unittest.main()
