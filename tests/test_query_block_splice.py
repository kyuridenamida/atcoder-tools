import unittest

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import predict_format
from atcodertools.fmtprediction.query_block_splice import (
    splice_query_definition_block,
)


def _content(blocks, sample_input):
    return ProblemContent(
        input_format_text=blocks[0],
        samples=[Sample(sample_input, None)],
        input_format_blocks=blocks,
    )


class QueryBlockSpliceTest(unittest.TestCase):

    def test_placeholder_lines_are_expanded(self):
        content = _content(
            [
                "N\nA_1 A_2 \\dots A_N\nQ\n"
                "\\mathrm{Query}_1\n\\vdots\n\\mathrm{Query}_Q\n",
                "l r",
            ],
            "4\n1 2 1 2\n2\n1 4\n2 3\n",
        )

        spliced = splice_query_definition_block(content)

        self.assertEqual(
            spliced.get_input_format(),
            "N\nA_1 A_2 \\dots A_N\nQ\nl_1 r_1\n\\vdots\nl_Q r_Q",
        )

    def test_row_index_suffix_is_dropped(self):
        # "X_i Y_i" の "_i" は行番号なので落とし、行番号を付け直す。
        content = _content(
            ["N\n\\text{query}_1\n\\vdots\n\\text{query}_N\n", "X_i Y_i"],
            "1\n1 2\n",
        )

        self.assertEqual(
            splice_query_definition_block(content).get_input_format(),
            "N\nX_1 Y_1\n\\vdots\nX_N Y_N",
        )

    def test_non_index_suffix_is_kept_as_part_of_the_name(self):
        # "h_1 h_2" は2つの別フィールドなので、潰して一意な名前にする。
        content = _content(
            ["N\n\\text{query}_1\n\\vdots\n\\text{query}_N\n", "h_1 h_2"],
            "1\n1 2\n",
        )

        self.assertEqual(
            splice_query_definition_block(content).get_input_format(),
            "N\nh1_1 h2_1\n\\vdots\nh1_N h2_N",
        )

    def test_prediction_uses_the_existing_parallel_pattern(self):
        content = _content(
            [
                "N\nA_1 A_2 \\dots A_N\nQ\n"
                "\\mathrm{Query}_1\n\\vdots\n\\mathrm{Query}_Q\n",
                "l r",
            ],
            "4\n1 2 1 2\n2\n1 4\n2 3\n",
        )

        self.assertEqual(
            str(predict_format(content).format),
            "[(Singular: N),(Parallel: A | 1 to N),"
            "(Singular: Q),(Parallel: l,r | 1 to Q)]",
        )

    def test_returns_none_for_unrelated_inputs(self):
        # ブロックが1つだけ / 2つ目が制約文 / プレースホルダが無い場合は対象外。
        single = _content(["N\nA_1 A_2 \\dots A_N\n"], "2\n1 2\n")
        self.assertIsNone(splice_query_definition_block(single))

        constraint = _content(
            ["N\n\\text{query}_1\n\\vdots\n\\text{query}_N\n",
                "1 \\leq l \\leq r"],
            "1\n1 2\n",
        )
        self.assertIsNone(splice_query_definition_block(constraint))

        no_placeholder = _content(["N\nA_1 A_2\n", "l r"], "1\n1 2\n")
        self.assertIsNone(splice_query_definition_block(no_placeholder))


if __name__ == "__main__":
    unittest.main()
