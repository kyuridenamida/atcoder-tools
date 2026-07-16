import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.models.input_specification import (
    InputSpecification,
    InputTokenKind,
    normalized_token_lines,
)


class TestLosslessInputSpecification(
    unittest.TestCase
):
    def test_preserves_query_block_boundaries_and_tags(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N Q\n"
                "A_1 A_2 \\ldots A_N\n"
                "\\text{query}_1\n"
                "\\text{query}_2\n"
                "\\vdots\n"
                "\\text{query}_Q\n"
            ),
            input_format_blocks=[
                (
                    "N Q\n"
                    "A_1 A_2 \\ldots A_N\n"
                    "\\text{query}_1\n"
                    "\\text{query}_2\n"
                    "\\vdots\n"
                    "\\text{query}_Q\n"
                ),
                "1 c\n",
                "2 l r\n",
            ],
            input_format_context_text=(
                "各クエリは以下のいずれかの"
                "形式で与えられる。"
            ),
            samples=[],
        )

        specification = (
            InputSpecification.from_problem_content(
                content
            )
        )

        self.assertEqual(
            3,
            len(specification.blocks),
        )

        self.assertEqual(
            [
                ["1", "c"],
            ],
            normalized_token_lines(
                specification
            )[1],
        )

        self.assertEqual(
            [
                ["2", "l", "r"],
            ],
            normalized_token_lines(
                specification
            )[2],
        )

        first_variant = (
            specification.blocks[1]
            .lines[0]
            .tokens
        )

        self.assertEqual(
            InputTokenKind.INTEGER,
            first_variant[0].kind,
        )

        self.assertEqual(
            "1",
            first_variant[0].raw_text,
        )

    def test_preserves_string_tag_candidates(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "Q\n"
                "operation_1\n"
                "\\vdots\n"
                "operation_Q\n"
            ),
            input_format_blocks=[
                (
                    "Q\n"
                    "operation_1\n"
                    "\\vdots\n"
                    "operation_Q\n"
                ),
                "Push x\n",
                "Pop\n",
                "Top\n",
            ],
            samples=[],
        )

        specification = (
            InputSpecification.from_problem_content(
                content
            )
        )

        normalized = normalized_token_lines(
            specification
        )

        self.assertEqual(
            [["Push", "x"]],
            normalized[1],
        )

        self.assertEqual(
            [["Pop"]],
            normalized[2],
        )

        self.assertEqual(
            InputTokenKind.WORD,
            specification.blocks[1]
            .lines[0]
            .tokens[0]
            .kind,
        )

    def test_preserves_ragged_row_boundaries(
        self,
    ):
        block = (
            "N\n"
            "M_1\n"
            "A_{1,1} \\ldots A_{1,M_1}\n"
            "\\vdots\n"
            "M_N\n"
            "A_{N,1} \\ldots A_{N,M_N}\n"
        )

        content = ProblemContent(
            input_format_text=block,
            samples=[],
        )

        specification = (
            InputSpecification.from_problem_content(
                content
            )
        )

        self.assertEqual(
            1,
            len(specification.blocks),
        )

        self.assertEqual(
            6,
            len(specification.blocks[0].lines),
        )

        third_line = (
            specification.blocks[0]
            .lines[2]
            .tokens
        )

        self.assertEqual(
            [
                "A_{1,1}",
                "...",
                "A_{1,M_1}",
            ],
            [
                token.normalized_text
                for token in third_line
            ],
        )

        self.assertEqual(
            InputTokenKind.ELLIPSIS,
            third_line[1].kind,
        )

    def test_preserves_raw_tex_and_normalizes_word(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "\\mathrm{query}_i : 1 c\n"
            ),
            samples=[],
        )

        specification = (
            InputSpecification.from_problem_content(
                content
            )
        )

        tokens = (
            specification.blocks[0]
            .lines[0]
            .tokens
        )

        self.assertEqual(
            "\\mathrm{query}_i",
            tokens[0].raw_text,
        )

        self.assertEqual(
            "query_i",
            tokens[0].normalized_text,
        )

        self.assertEqual(
            InputTokenKind.DELIMITER,
            tokens[1].kind,
        )

    def test_falls_back_to_legacy_input_format(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N\n"
                "A_1 \\ldots A_N\n"
            ),
            input_format_blocks=[],
            samples=[],
        )

        specification = (
            InputSpecification.from_problem_content(
                content
            )
        )

        self.assertEqual(
            1,
            len(specification.blocks),
        )

        self.assertEqual(
            2,
            len(specification.blocks[0].lines),
        )


if __name__ == "__main__":
    unittest.main()
