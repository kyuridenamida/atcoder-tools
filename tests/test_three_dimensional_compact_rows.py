import subprocess
import sys
import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
    get_builtin_code_generator_info_toml_path,
)
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.common.language import PYTHON
from atcodertools.fmtprediction.models.format import (
    ThreeDimensionalPattern,
    TwoDimensionalPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)


FIXED_COMPACT_FORMAT = """
P_{1,1,1}P_{1,1,2}P_{1,1,3}P_{1,1,4}
P_{1,2,1}P_{1,2,2}P_{1,2,3}P_{1,2,4}
P_{1,3,1}P_{1,3,2}P_{1,3,3}P_{1,3,4}
P_{1,4,1}P_{1,4,2}P_{1,4,3}P_{1,4,4}
P_{2,1,1}P_{2,1,2}P_{2,1,3}P_{2,1,4}
P_{2,2,1}P_{2,2,2}P_{2,2,3}P_{2,2,4}
P_{2,3,1}P_{2,3,2}P_{2,3,3}P_{2,3,4}
P_{2,4,1}P_{2,4,2}P_{2,4,3}P_{2,4,4}
P_{3,1,1}P_{3,1,2}P_{3,1,3}P_{3,1,4}
P_{3,2,1}P_{3,2,2}P_{3,2,3}P_{3,2,4}
P_{3,3,1}P_{3,3,2}P_{3,3,3}P_{3,3,4}
P_{3,4,1}P_{3,4,2}P_{3,4,3}P_{3,4,4}
""".strip()

FIXED_COMPACT_SAMPLE = """
####
....
#...
.#..
..#.
...#
##..
..##
#.#.
.#.#
###.
...#
""".strip()

VARIABLE_COMPACT_FORMAT = r"""
D H W
A_{1,1,1}A_{1,1,2}\ldots A_{1,1,W}
A_{1,2,1}A_{1,2,2}\ldots A_{1,2,W}
\vdots
A_{1,H,1}A_{1,H,2}\ldots A_{1,H,W}
\vdots
A_{D,H,1}A_{D,H,2}\ldots A_{D,H,W}
""".strip()

VARIABLE_COMPACT_SAMPLE = """
2 2 3
.#.
###
..#
#..
""".strip()

VARIABLE_SPACED_FORMAT = r"""
D H W
A_{1,1,1} A_{1,1,2} \ldots A_{1,1,W}
A_{1,2,1} A_{1,2,2} \ldots A_{1,2,W}
\vdots
A_{1,H,1} A_{1,H,2} \ldots A_{1,H,W}
\vdots
A_{D,H,1} A_{D,H,2} \ldots A_{D,H,W}
""".strip()

VARIABLE_SPACED_SAMPLE = """
2 2 3
. # .
# # #
. . #
# . .
""".strip()


def content(input_format, sample_input):
    return ProblemContent(
        input_format_text=input_format,
        input_format_blocks=[input_format],
        input_format_context_text="",
        original_html="",
        samples=[Sample(sample_input, "")],
    )


class TestThreeDimensionalCompactRows(unittest.TestCase):
    def test_fixed_compact_rows_collapse_innermost_dimension(self):
        result = predict_format(
            content(
                FIXED_COMPACT_FORMAT,
                FIXED_COMPACT_SAMPLE,
            )
        )

        self.assertEqual(1, len(result.format.sequence))
        pattern = result.format.sequence[0]

        self.assertIsInstance(
            pattern,
            TwoDimensionalPattern,
        )
        self.assertEqual("P", pattern.var.name)
        self.assertEqual(Type.str, pattern.var.type)
        self.assertEqual(2, pattern.var.dim_num())

    def test_variable_compact_rows_collapse_innermost_dimension(self):
        result = predict_format(
            content(
                VARIABLE_COMPACT_FORMAT,
                VARIABLE_COMPACT_SAMPLE,
            )
        )
        pattern = result.format.sequence[-1]

        self.assertIsInstance(
            pattern,
            TwoDimensionalPattern,
        )
        self.assertEqual("A", pattern.var.name)
        self.assertEqual(Type.str, pattern.var.type)
        self.assertEqual(2, pattern.var.dim_num())

    def test_spaced_character_elements_remain_three_dimensional(self):
        result = predict_format(
            content(
                VARIABLE_SPACED_FORMAT,
                VARIABLE_SPACED_SAMPLE,
            )
        )
        pattern = result.format.sequence[-1]

        self.assertIsInstance(
            pattern,
            ThreeDimensionalPattern,
        )
        self.assertEqual("A", pattern.var.name)
        self.assertEqual(Type.str, pattern.var.type)
        self.assertEqual(3, pattern.var.dim_num())

    def test_generated_python_reads_compact_rows(self):
        result = predict_format(
            content(
                FIXED_COMPACT_FORMAT,
                FIXED_COMPACT_SAMPLE,
            )
        )

        generator = UniversalCodeGenerator(
            result.format,
            CodeStyleConfig(
                lang=PYTHON.name
            ),
            get_builtin_code_generator_info_toml_path(
                PYTHON.name
            ),
        )
        parameters = generator.generate_parameters()

        self.assertIn(
            "List[List[str]]",
            parameters["formal_arguments"],
        )

        generated = "\n".join(
            [
                "#!/usr/bin/env python3",
                "from typing import *",
                "import sys",
                "",
                "def solve(P):",
                (
                    "    print("
                    "len(P), len(P[0]), P[0][0]"
                    ")"
                ),
                "",
                "tokens = iter(sys.stdin.read().split())",
                parameters["input_part"],
                "solve(P)",
                "",
            ]
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                generated,
            ],
            input=FIXED_COMPACT_SAMPLE,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(
            0,
            completed.returncode,
            msg=completed.stderr + "\n" + generated,
        )
        self.assertEqual(
            "3 4 ####",
            completed.stdout.strip(),
        )


if __name__ == "__main__":
    unittest.main()
