import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.tagged_query import (
    MultipleTaggedQueryPredictionsError,
    _query_count_candidates,
    predict_tagged_queries,
)


def unique_scalar_content():
    input_format = (
        "Q\n"
        "item_1\n"
        "...\n"
        "item_Q\n"
    )

    content = ProblemContent(
        input_format_text=input_format,
        samples=[
            Sample(
                "3\n1 10\n2\n1 20\n",
                "",
            ),
            Sample(
                "2\n2\n1 30\n",
                "",
            ),
        ],
    )

    content.input_format_blocks = [
        input_format,
        "1 x\n",
        "2\n",
    ]

    return content


def ambiguous_scalar_content():
    input_format = (
        "N Q\n"
        "item_1\n"
        "...\n"
        "item_Q\n"
    )

    content = ProblemContent(
        input_format_text=input_format,
        samples=[
            Sample(
                "2 2\n1 10\n2\n",
                "",
            ),
            Sample(
                "3 3\n1 20\n2\n1 30\n",
                "",
            ),
        ],
    )

    content.input_format_blocks = [
        input_format,
        "1 x\n",
        "2\n",
    ]

    return content


class TestTaggedQueryScalarCountFallback(
    unittest.TestCase
):
    def test_uses_unique_validated_scalar(self):
        content = unique_scalar_content()

        self.assertEqual(
            set(),
            _query_count_candidates(content),
        )

        prediction = predict_tagged_queries(
            content
        )

        self.assertEqual(
            "Q",
            prediction.format.query_count_var,
        )

        self.assertEqual(
            (3, 2),
            prediction.sample_query_counts,
        )

    def test_rejects_ambiguous_scalars(self):
        content = ambiguous_scalar_content()

        self.assertEqual(
            set(),
            _query_count_candidates(content),
        )

        with self.assertRaises(
            MultipleTaggedQueryPredictionsError
        ):
            predict_tagged_queries(content)


if __name__ == "__main__":
    unittest.main()
