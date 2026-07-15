import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.format import (
    ThreeDimensionalPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)
from atcodertools.fmtprediction.predict_simple_format import (
    predict_simple_format,
)
from atcodertools.fmtprediction.tokenize_format import (
    search_formats_with_minimum_vars,
)


INPUT_FORMAT = """
D H W
A_{1,1,1} ... A_{1,1,W}
A_{1,H,1} ... A_{1,H,W}
...
A_{D,1,1} ... A_{D,1,W}
A_{D,H,1} ... A_{D,H,W}
"""

SAMPLE_INPUT = """
2 2 3
1 2 3
4 5 6
7 8 9
10 11 12
"""


class TestThreeDimensionalPrediction(unittest.TestCase):
    def test_tokenizer_finds_three_indices(self):
        candidates = (
            search_formats_with_minimum_vars(
                INPUT_FORMAT
            )
        )

        matching = [
            candidate
            for candidate in candidates
            if any(
                token.var_name == "A"
                and token.dim_num() == 3
                and token.first_index == "1"
                and token.second_index == "1"
                and token.third_index == "1"
                for token in candidate.var_tokens
            )
        ]

        self.assertTrue(matching)

    def test_simple_format_contains_3d_pattern(self):
        candidates = (
            search_formats_with_minimum_vars(
                INPUT_FORMAT
            )
        )

        tokenized = next(
            candidate
            for candidate in candidates
            if any(
                token.var_name == "A"
                and token.dim_num() == 3
                for token in candidate.var_tokens
            )
        )

        format_ = predict_simple_format(
            tokenized.var_tokens
        )

        pattern = format_.sequence[-1]

        self.assertIsInstance(
            pattern,
            ThreeDimensionalPattern,
        )
        self.assertEqual(3, pattern.var.dim_num())

    def test_end_to_end_type_prediction(self):
        content = ProblemContent(
            INPUT_FORMAT,
            [Sample(SAMPLE_INPUT, None)],
        )

        result = predict_format(content)
        format_ = result.format
        pattern = format_.sequence[-1]

        self.assertIsInstance(
            pattern,
            ThreeDimensionalPattern,
        )
        self.assertEqual(
            ["D", "H", "W", "A"],
            [
                variable.name
                for variable in format_.all_vars()
            ],
        )
        self.assertEqual(Type.int, pattern.var.type)
        self.assertEqual(3, pattern.var.dim_num())
        self.assertIsNotNone(
            pattern.var.third_index
        )


if __name__ == "__main__":
    unittest.main()
