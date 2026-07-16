import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.homogeneous_query import (
    NoHomogeneousQueryPredictionError,
    predict_homogeneous_queries,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryValueType,
)


def make_content():
    content = ProblemContent(
        input_format_text=(
            "N Q\n"
            "query_1\n"
            "...\n"
            "query_Q\n"
        ),
        samples=[
            Sample(
                (
                    "5 2\n"
                    "1 3\n"
                    "2 5\n"
                ),
                "",
            ),
            Sample(
                (
                    "8 1\n"
                    "4 7\n"
                ),
                "",
            ),
        ],
    )

    content.input_format_blocks = [
        (
            "N Q\n"
            "query_1\n"
            "...\n"
            "query_Q\n"
        ),
        "L R\n",
    ]

    return content


class TestHomogeneousQueryPrediction(
    unittest.TestCase
):
    def test_predicts_fixed_query_rows(
        self,
    ):
        prediction = (
            predict_homogeneous_queries(
                make_content()
            )
        )

        self.assertEqual(
            "Q",
            prediction
            .format
            .query_count_var,
        )

        self.assertEqual(
            ["L", "R"],
            [
                argument.name
                for argument
                in prediction
                .format
                .arguments
            ],
        )

        self.assertEqual(
            [
                TaggedQueryValueType.INT,
                TaggedQueryValueType.INT,
            ],
            [
                argument.type
                for argument
                in prediction
                .format
                .arguments
            ],
        )

        self.assertEqual(
            (2, 1),
            prediction.sample_query_counts,
        )

    def test_rejects_extra_definition_block(
        self,
    ):
        content = make_content()

        content.input_format_blocks.append(
            "suffix\n"
        )

        with self.assertRaises(
            NoHomogeneousQueryPredictionError
        ):
            predict_homogeneous_queries(
                content
            )


if __name__ == "__main__":
    unittest.main()
