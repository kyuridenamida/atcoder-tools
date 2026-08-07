import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryValueType,
)
from atcodertools.fmtprediction.tagged_query import (
    NoTaggedQueryPredictionError,
    predict_tagged_queries,
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
                    "5 4\n"
                    "1 10\n"
                    "2 hello 20\n"
                    "1 30\n"
                    "2 world 40\n"
                ),
                "",
            ),
            Sample(
                (
                    "8 2\n"
                    "1 50\n"
                    "2 tagged 60\n"
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
        "1 x\n",
        "2 s y\n",
    ]

    content.input_format_context_text = (
        "Each query is 1 x or 2 s y."
    )

    return content


class TestTaggedQueryPrediction(
    unittest.TestCase
):
    def test_predicts_numeric_variants(
        self,
    ):
        prediction = predict_tagged_queries(
            make_content()
        )

        self.assertEqual(
            "Q",
            prediction
            .format
            .query_count_var,
        )

        self.assertEqual(
            [1, 2],
            [
                variant.tag
                for variant
                in prediction
                .format
                .variants
            ],
        )

        self.assertEqual(
            [
                TaggedQueryValueType.INT,
            ],
            [
                argument.type
                for argument
                in prediction
                .format
                .variants[0]
                .arguments
            ],
        )

        self.assertEqual(
            [
                TaggedQueryValueType.STRING,
                TaggedQueryValueType.INT,
            ],
            [
                argument.type
                for argument
                in prediction
                .format
                .variants[1]
                .arguments
            ],
        )

        self.assertEqual(
            (4, 2),
            prediction.sample_query_counts,
        )

    def test_rejects_unknown_tag(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N Q\n"
                "query_1\n"
                "...\n"
                "query_Q\n"
            ),
            samples=[
                Sample(
                    "5 1\n3 10\n",
                    "",
                ),
            ],
        )

        content.input_format_blocks = [
            "N Q\nquery_1\n...\nquery_Q\n",
            "1 x\n",
            "2 y\n",
        ]

        with self.assertRaises(
            NoTaggedQueryPredictionError
        ):
            predict_tagged_queries(
                content
            )


if __name__ == "__main__":
    unittest.main()
