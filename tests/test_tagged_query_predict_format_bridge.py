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
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
    TaggedQueryValueType,
)
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)


def tagged_query_content():
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
                    "1 10 20\n"
                    "2\n"
                    "1 30 40\n"
                    "2\n"
                ),
                "",
            ),
            Sample(
                (
                    "8 2\n"
                    "2\n"
                    "1 50 60\n"
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
        "1 x y\n",
        "2\n",
    ]

    return content


def zero_length_prefix_content():
    content = ProblemContent(
        input_format_text=(
            "N Q\n"
            "A_1 ... A_{N-1}\n"
            "query_1\n"
            "...\n"
            "query_Q\n"
        ),
        samples=[
            Sample(
                (
                    "1 2\n"
                    "1 10\n"
                    "2\n"
                ),
                "",
            ),
            Sample(
                (
                    "3 1\n"
                    "7 8\n"
                    "1 20\n"
                ),
                "",
            ),
        ],
    )

    content.input_format_blocks = [
        (
            "N Q\n"
            "A_1 ... A_{N-1}\n"
            "query_1\n"
            "...\n"
            "query_Q\n"
        ),
        "1 x\n",
        "2\n",
    ]

    return content


def ordinary_content():
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


class TestTaggedQueryPredictFormatBridge(
    unittest.TestCase
):
    def test_tagged_query_uses_fallback(
        self,
    ):
        result = predict_format(
            tagged_query_content()
        )

        self.assertIsInstance(
            result.format,
            TaggedQueryFormat,
        )

        self.assertEqual(
            "Q",
            result.format.query_count_var,
        )

        self.assertEqual(
            [1, 2],
            [
                variant.tag
                for variant
                in result.format.variants
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
                in result
                .format
                .variants[0]
                .arguments
            ],
        )

        self.assertEqual(
            [
                "N",
                "Q",
            ],
            [
                variable.name
                for variable
                in result
                .format
                .prefix_format
                .all_vars()
            ],
        )

    def test_zero_length_prefix_array_merges_types(
        self,
    ):
        result = predict_format(
            zero_length_prefix_content()
        )

        self.assertIsInstance(
            result.format,
            TaggedQueryFormat,
        )

        self.assertEqual(
            [
                "N",
                "Q",
                "A",
            ],
            [
                variable.name
                for variable
                in result
                .format
                .prefix_format
                .all_vars()
            ],
        )

        self.assertTrue(
            all(
                variable.type is not None
                for variable
                in result
                .format
                .prefix_format
                .all_vars()
            )
        )

    def test_ordinary_format_is_unchanged(
        self,
    ):
        result = predict_format(
            ordinary_content()
        )

        self.assertNotIsInstance(
            result.format,
            TaggedQueryFormat,
        )

        self.assertNotIsInstance(
            result.format,
            RaggedRowFormat,
        )


if __name__ == "__main__":
    unittest.main()
