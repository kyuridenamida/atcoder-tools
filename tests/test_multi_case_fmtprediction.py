import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.predict_multi_case_format import (
    NoMultiCaseFormatFoundError,
    predict_multi_case_format,
)


class TestMultiCaseProblemContent(unittest.TestCase):
    def test_extracts_multiple_blocks_and_keeps_legacy_api(
        self,
    ):
        html = """
        <html>
          <body>
            <section>
              <h3>入力</h3>
              <p>その後、T 個のテストケースが続く。</p>
              <pre>T</pre>
              <pre>N
A_1 A_2 ... A_N</pre>
            </section>
            <section>
              <h3>入力例 1</h3>
              <pre>2
3
1 2 3
1
9</pre>
            </section>
            <section>
              <h3>出力例 1</h3>
              <pre>6
9</pre>
            </section>
          </body>
        </html>
        """

        content = ProblemContent.from_html(html)

        self.assertEqual(
            "T\n",
            content.get_input_format(),
        )
        self.assertEqual(
            [
                "T\n",
                "N\nA_1 A_2 ... A_N\n",
            ],
            content.get_input_format_blocks(),
        )

    def test_single_block_remains_single_block(self):
        content = ProblemContent(
            "N\nA_1 A_2 ... A_N\n",
            [
                Sample(
                    "3\n1 2 3\n",
                    "",
                )
            ],
        )

        self.assertEqual(
            ["N\nA_1 A_2 ... A_N\n"],
            content.get_input_format_blocks(),
        )


class TestMultiCaseFormatPrediction(unittest.TestCase):
    def test_split_layout(self):
        content = ProblemContent(
            input_format_text="T\n",
            input_format_blocks=[
                "T\n",
                "N\nA_1 A_2 ... A_N\n",
            ],
            input_format_context_text=(
                "T 個のテストケースが与えられる。"
            ),
            samples=[
                Sample(
                    "2\n3\n1 2 3\n1\n9\n",
                    "",
                )
            ],
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual("split", result.layout)
        self.assertEqual("T", result.case_count_var)
        self.assertEqual(Type.int, result.var_to_type["A"])

    def test_count_variable_is_not_hard_coded(self):
        content = ProblemContent(
            input_format_text="Q\n",
            input_format_blocks=[
                "Q\n",
                "X Y\n",
            ],
            input_format_context_text=(
                "Q test cases follow."
            ),
            samples=[
                Sample(
                    "2\n1 alpha\n2 beta\n",
                    "",
                )
            ],
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual("Q", result.case_count_var)
        self.assertEqual(Type.str, result.var_to_type["Y"])

    def test_wrapper_test_placeholder_layout(self):
        content = ProblemContent(
            input_format_text=(
                "T\n"
                "\\text{test}_1\n"
                "\\text{test}_2\n"
                "\\vdots\n"
                "\\text{test}_T\n"
            ),
            input_format_blocks=[
                (
                    "T\n"
                    "\\text{test}_1\n"
                    "\\text{test}_2\n"
                    "\\vdots\n"
                    "\\text{test}_T\n"
                ),
                "N\nA_1 A_2 ... A_N\n",
            ],
            input_format_context_text=(
                "各テストケースは以下の形式で与えられる。"
            ),
            samples=[
                Sample(
                    "2\n3\n1 2 3\n1\n9\n",
                    "",
                )
            ],
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual("wrapper", result.layout)
        self.assertEqual("T", result.case_count_var)
        self.assertEqual(Type.int, result.var_to_type["A"])

    def test_wrapper_case_tex_commands_layout(self):
        content = ProblemContent(
            input_format_text=(
                "T\n"
                "\\rm{case}_{1}\n"
                "\\rm{case}_{2}\n"
                "\\vdots\n"
                "\\rm{case}_{\\it{T}}\n"
            ),
            input_format_blocks=[
                (
                    "T\n"
                    "\\rm{case}_{1}\n"
                    "\\rm{case}_{2}\n"
                    "\\vdots\n"
                    "\\rm{case}_{\\it{T}}\n"
                ),
                "S L R\n",
            ],
            samples=[
                Sample(
                    "2\n0295 295 295\n22 23 234\n",
                    "",
                )
            ],
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual("wrapper", result.layout)
        self.assertEqual("T", result.case_count_var)
        self.assertEqual(Type.str, result.var_to_type["S"])

    def test_single_block_indexed_layout(self):
        content = ProblemContent(
            input_format_text=(
                "Q\n"
                "H_1 W_1 K_1\n"
                "H_2 W_2 K_2\n"
                "\\vdots\n"
                "H_Q W_Q K_Q\n"
            ),
            input_format_blocks=[
                (
                    "Q\n"
                    "H_1 W_1 K_1\n"
                    "H_2 W_2 K_2\n"
                    "\\vdots\n"
                    "H_Q W_Q K_Q\n"
                )
            ],
            input_format_context_text=(
                "Q 個のテストケースが与えられる。"
                "各テストケースは H, W, K からなる。"
            ),
            samples=[
                Sample(
                    (
                        "3\n"
                        "3 4 3\n"
                        "2 2 3\n"
                        "1000 800 3000\n"
                    ),
                    "",
                )
            ],
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual(
            "single_block_indexed",
            result.layout,
        )
        self.assertEqual("Q", result.case_count_var)
        self.assertEqual(Type.int, result.var_to_type["H"])
        self.assertEqual(Type.int, result.var_to_type["W"])
        self.assertEqual(Type.int, result.var_to_type["K"])

    def test_indexed_layout_uses_problem_statement_prose(
        self,
    ):
        # The testcase declaration may be outside the input section, as in
        # PAKEN Camp 2023 Day 1 N.
        original_html = """
        <html>
          <body>
            <section>
              <h3>問題文</h3>
              <p>Q 個のテストケースに対して答えてください。</p>
            </section>
            <section>
              <h3>入力</h3>
              <p>入力は以下の形式で与えられる。</p>
              <pre>Q
H_1 W_1 K_1
H_2 W_2 K_2
\\vdots
H_Q W_Q K_Q</pre>
            </section>
            <section>
              <h3>入力例 1</h3>
              <pre>3
3 4 3
2 2 3
1000 800 3000</pre>
            </section>
            <section>
              <h3>出力例 1</h3>
              <pre>Alice
Bob
Alice</pre>
            </section>
          </body>
        </html>
        """

        content = ProblemContent.from_html(
            original_html
        )

        result = predict_multi_case_format(
            content
        )

        self.assertEqual(
            "single_block_indexed",
            result.layout,
        )
        self.assertEqual(
            "Q",
            result.case_count_var,
        )

    def test_distant_unrelated_case_word_is_not_evidence(
        self,
    ):
        # Merely having the count variable and the phrase "test cases"
        # somewhere in the page is insufficient. They must occur in one
        # bounded testcase-count expression.
        content = ProblemContent(
            input_format_text=(
                "Q\n"
                "H_1 W_1 K_1\n"
                "H_2 W_2 K_2\n"
                "...\n"
                "H_Q W_Q K_Q\n"
            ),
            input_format_blocks=[
                (
                    "Q\n"
                    "H_1 W_1 K_1\n"
                    "H_2 W_2 K_2\n"
                    "...\n"
                    "H_Q W_Q K_Q\n"
                )
            ],
            input_format_context_text="",
            original_html=(
                "<p>Q is an input value.</p>"
                "<p>"
                + ("unrelated " * 30)
                + "</p>"
                "<p>Some examples discuss test cases.</p>"
            ),
            samples=[
                Sample(
                    "2\n3 4 3\n2 2 3\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_multirow_indexed_arrays_are_not_testcases_without_prose(
        self,
    ):
        # This is an ordinary pair of arrays, not n independent
        # testcases. Its structure is intentionally identical to the
        # false-positive found in the historical regression corpus.
        content = ProblemContent(
            input_format_text=(
                "n\n"
                "p_1 l_1\n"
                "p_2 l_2\n"
                "...\n"
                "p_n l_n\n"
            ),
            input_format_blocks=[
                (
                    "n\n"
                    "p_1 l_1\n"
                    "p_2 l_2\n"
                    "...\n"
                    "p_n l_n\n"
                )
            ],
            input_format_context_text=(
                "n 個の要素からなる二つの列 p, l が与えられる。"
            ),
            samples=[
                Sample(
                    "2\n0 3\n1 2\n",
                    "",
                ),
                Sample(
                    "1\n0 3\n",
                    "",
                ),
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_ordinary_array_is_not_misclassified(self):
        content = ProblemContent(
            input_format_text=(
                "N\nA_1 A_2 ... A_N\n"
            ),
            input_format_blocks=[
                "N\nA_1 A_2 ... A_N\n"
            ],
            samples=[
                Sample(
                    "3\n1 2 3\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_malformed_wrapper_is_rejected(self):
        content = ProblemContent(
            input_format_text=(
                "T\n"
                "N_1\n"
                "N_2\n"
                "\\vdots\n"
                "N_T\n"
            ),
            input_format_blocks=[
                (
                    "T\n"
                    "N_1\n"
                    "N_2\n"
                    "\\vdots\n"
                    "N_T\n"
                ),
                "X\n",
            ],
            samples=[
                Sample(
                    "2\n10\n20\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_two_blocks_without_evidence_are_rejected(self):
        content = ProblemContent(
            input_format_text="N\n",
            input_format_blocks=[
                "N\n",
                "X\n",
            ],
            input_format_context_text=(
                "The first value is N."
            ),
            samples=[
                Sample(
                    "2\n10\n20\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_wrong_case_count_is_rejected(self):
        content = ProblemContent(
            input_format_text="T\n",
            input_format_blocks=[
                "T\n",
                "X\n",
            ],
            input_format_context_text=(
                "T test cases follow."
            ),
            samples=[
                Sample(
                    "3\n10\n20\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_extra_tokens_are_rejected(self):
        content = ProblemContent(
            input_format_text="T\n",
            input_format_blocks=[
                "T\n",
                "X\n",
            ],
            input_format_context_text=(
                "T test cases follow."
            ),
            samples=[
                Sample(
                    "2\n10\n20\n30\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_non_integer_count_is_rejected(self):
        content = ProblemContent(
            input_format_text="T\n",
            input_format_blocks=[
                "T\n",
                "X\n",
            ],
            input_format_context_text=(
                "T test cases follow."
            ),
            samples=[
                Sample(
                    "2.5\n10\n20\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)

    def test_excessive_count_is_rejected_without_looping(self):
        content = ProblemContent(
            input_format_text="T\n",
            input_format_blocks=[
                "T\n",
                "X\n",
            ],
            input_format_context_text=(
                "T test cases follow."
            ),
            samples=[
                Sample(
                    "100001\n",
                    "",
                )
            ],
        )

        with self.assertRaises(
            NoMultiCaseFormatFoundError
        ):
            predict_multi_case_format(content)


if __name__ == "__main__":
    unittest.main()
