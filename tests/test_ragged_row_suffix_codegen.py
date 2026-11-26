import json
import subprocess
import sys
import unittest
from pathlib import Path

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.models.format_prediction_result import (
    FormatPredictionResult,
)
from atcodertools.fmtprediction.ragged_row import (
    predict_same_line_ragged_rows,
)


ROOT = Path(__file__).resolve().parents[1]

TOML_ROOT = (
    ROOT
    / "atcodertools"
    / "codegen"
    / "code_generators"
    / "universal_generator"
)

LANGUAGES = (
    "cpp",
    "cs",
    "d",
    "go",
    "java",
    "julia",
    "nim",
    "python",
    "rust",
    "swift",
)


class _Config:
    def indent(
        self,
        depth,
    ):
        return " " * 4 * depth


def make_content():
    return ProblemContent(
        input_format_text=(
            "N Q\n"
            "L_1 a_{1,1} "
            "... a_{1,L_1}\n"
            "...\n"
            "L_N a_{N,1} "
            "... a_{N,L_N}\n"
            "s_1 t_1\n"
            "...\n"
            "s_Q t_Q\n"
        ),
        samples=[
            Sample(
                (
                    "2 2\n"
                    "2 10 20\n"
                    "1 30\n"
                    "1 1\n"
                    "2 1\n"
                ),
                "",
            ),
        ],
    )


def make_result():
    prediction = (
        predict_same_line_ragged_rows(
            make_content()
        )
    )

    result = (
        FormatPredictionResult
        .create_ragged_row_typed_format(
            prediction.prefix_format,
            prediction.schema,
            prediction.var_to_type,
            prediction.suffix_format,
        )
    )

    return prediction, result


class TestRaggedRowSuffixCodegen(
    unittest.TestCase
):
    def test_suffix_format_is_predicted(
        self,
    ):
        prediction, result = make_result()

        self.assertEqual(
            "[(Parallel: s,t | 1 to Q)]",
            str(
                prediction.suffix_format
            ),
        )

        self.assertEqual(
            "[(Parallel: s,t | 1 to Q)]",
            str(
                result.format.suffix_format
            ),
        )

        self.assertEqual(
            [
                "N",
                "Q",
                "L",
                "a",
                "s",
                "t",
            ],
            [
                variable.name
                for variable
                in result.format.all_vars()
            ],
        )

    def test_all_ten_languages_include_suffix(
        self,
    ):
        _, result = make_result()

        for language in LANGUAGES:
            with self.subTest(
                language=language
            ):
                generator = (
                    UniversalCodeGenerator(
                        result.format,
                        _Config(),
                        (
                            TOML_ROOT
                            / "{}.toml".format(
                                language
                            )
                        ),
                    )
                )

                parameters = (
                    generator
                    .generate_parameters()
                )

                self.assertIn(
                    "s",
                    parameters[
                        "formal_arguments"
                    ],
                )

                self.assertIn(
                    "t",
                    parameters[
                        "formal_arguments"
                    ],
                )

                self.assertIn(
                    "s",
                    parameters[
                        "actual_arguments"
                    ],
                )

                self.assertIn(
                    "t",
                    parameters[
                        "actual_arguments"
                    ],
                )

    def test_python_reads_prefix_ragged_and_suffix(
        self,
    ):
        _, result = make_result()

        generator = UniversalCodeGenerator(
            result.format,
            _Config(),
            TOML_ROOT / "python.toml",
        )

        parameters = (
            generator.generate_parameters()
        )

        suffix_lines = [
            line
            for line in (
                parameters["input_part"]
                .splitlines()
            )
            if "s = [" in line
        ]

        self.assertEqual(
            1,
            len(suffix_lines),
        )

        self.assertTrue(
            suffix_lines[0].startswith(
                "    "
            )
        )

        program = "\n".join(
            [
                "import json",
                "import sys",
                "def main():",
                (
                    "    tokens = iter("
                    "sys.stdin.read().split())"
                ),
                (
                    "    "
                    + parameters["input_part"]
                ),
                (
                    "    remaining = "
                    "list(tokens)"
                ),
                (
                    "    print(json.dumps("
                    "[N, Q, L, a, s, t, "
                    "remaining]))"
                ),
                "main()",
            ]
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                program,
            ],
            input=(
                "2 2\n"
                "2 10 20\n"
                "1 30\n"
                "1 1\n"
                "2 1\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        self.assertEqual(
            [
                2,
                2,
                [2, 1],
                [
                    [10, 20],
                    [30],
                ],
                [1, 2],
                [1, 1],
                [],
            ],
            json.loads(
                completed.stdout
            ),
        )


if __name__ == "__main__":
    unittest.main()
