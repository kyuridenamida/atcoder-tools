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
from atcodertools.fmtprediction.two_line_ragged_row import (
    predict_two_line_ragged_rows,
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


class Config:
    def indent(
        self,
        depth,
    ):
        return " " * 4 * depth


def content():
    return ProblemContent(
        input_format_text=(
            "N K\n"
            "d_1\n"
            "A_{1,1} ... A_{1,d_1}\n"
            "...\n"
            "d_K\n"
            "A_{K,1} ... A_{K,d_K}\n"
        ),
        samples=[
            Sample(
                (
                    "4 3\n"
                    "2\n"
                    "1 2\n"
                    "1\n"
                    "3\n"
                    "2\n"
                    "2 4\n"
                ),
                "",
            ),
        ],
    )


def result():
    prediction = (
        predict_two_line_ragged_rows(
            content()
        )
    )

    typed = (
        FormatPredictionResult
        .create_ragged_row_typed_format(
            prediction.prefix_format,
            prediction.schema,
            prediction.var_to_type,
            prediction.suffix_format,
        )
    )

    return prediction, typed


class TestTwoLineRaggedRowPrediction(
    unittest.TestCase
):
    def test_predicts_two_line_schema(
        self,
    ):
        prediction, typed = result()

        self.assertEqual(
            "K",
            prediction.schema.row_count_var,
        )

        self.assertEqual(
            ("d",),
            prediction.schema.prefix_fields,
        )

        self.assertEqual(
            "A",
            prediction.schema.values_name,
        )

        self.assertEqual(
            [
                "N",
                "K",
                "d",
                "A",
            ],
            [
                variable.name
                for variable
                in typed.format.all_vars()
            ],
        )

    def test_all_languages_generate_parameters(
        self,
    ):
        _, typed = result()

        for language in LANGUAGES:
            with self.subTest(
                language=language
            ):
                generator = (
                    UniversalCodeGenerator(
                        typed.format,
                        Config(),
                        TOML_ROOT
                        / "{}.toml".format(
                            language
                        ),
                    )
                )

                parameters = (
                    generator
                    .generate_parameters()
                )

                self.assertTrue(
                    parameters[
                        "prediction_success"
                    ]
                )

                self.assertIn(
                    "d",
                    parameters[
                        "formal_arguments"
                    ],
                )

                self.assertIn(
                    "A",
                    parameters[
                        "formal_arguments"
                    ],
                )

    def test_python_consumes_input(
        self,
    ):
        _, typed = result()

        generator = UniversalCodeGenerator(
            typed.format,
            Config(),
            TOML_ROOT / "python.toml",
        )

        parameters = (
            generator.generate_parameters()
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
                    "    print(json.dumps("
                    "[N, K, d, A, "
                    "list(tokens)]))"
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
                "4 3\n"
                "2\n"
                "1 2\n"
                "1\n"
                "3\n"
                "2\n"
                "2 4\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        self.assertEqual(
            [
                4,
                3,
                [2, 1, 2],
                [
                    [1, 2],
                    [3],
                    [2, 4],
                ],
                [],
            ],
            json.loads(
                completed.stdout
            ),
        )


if __name__ == "__main__":
    unittest.main()
