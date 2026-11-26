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
from atcodertools.codegen.ragged_row_contract import (
    RaggedCodegenContractNotFoundError,
)
from atcodertools.fmtprediction.models.format_prediction_result import (
    FormatPredictionResult,
)
from atcodertools.fmtprediction.models.ragged_format import (
    RaggedRowFormat,
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
    def __init__(
        self,
        indent_width=4,
    ):
        self.indent_width = indent_width

    def indent(self, depth):
        return (
            " " * self.indent_width * depth
        )


def make_ragged_result():
    content = ProblemContent(
        input_format_text=(
            "N\n"
            "L_1 a_{1,1} "
            "... a_{1,L_1}\n"
            "...\n"
            "L_N a_{N,1} "
            "... a_{N,L_N}\n"
        ),
        samples=[
            Sample(
                (
                    "3\n"
                    "2 10 20\n"
                    "1 30\n"
                    "3 40 50 60\n"
                ),
                "",
            ),
        ],
    )

    prediction = (
        predict_same_line_ragged_rows(
            content
        )
    )

    return (
        FormatPredictionResult
        .create_ragged_row_typed_format(
            prediction.prefix_format,
            prediction.schema,
            prediction.var_to_type,
        )
    )


class TestRaggedRowUniversalCodegen(
    unittest.TestCase
):
    def test_typed_result_uses_ragged_format(
        self,
    ):
        result = make_ragged_result()

        self.assertIsInstance(
            result.format,
            RaggedRowFormat,
        )

        self.assertEqual(
            ["N", "L", "a"],
            [
                variable.name
                for variable
                in result.format.all_vars()
            ],
        )

        self.assertEqual(
            [0, 1, 2],
            [
                variable.dim_num()
                for variable
                in result.format.all_vars()
            ],
        )

    def test_all_ten_builtin_languages_generate_parameters(
        self,
    ):
        result = make_ragged_result()

        self.assertEqual(
            10,
            len(LANGUAGES),
        )

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

                self.assertTrue(
                    parameters[
                        "prediction_success"
                    ]
                )

                self.assertTrue(
                    parameters["ragged_row"]
                )

                self.assertFalse(
                    parameters["multi_case"]
                )

                self.assertTrue(
                    parameters[
                        "formal_arguments"
                    ]
                )

                self.assertTrue(
                    parameters[
                        "actual_arguments"
                    ]
                )

                self.assertTrue(
                    parameters["input_part"]
                )

                self.assertIn(
                    "L",
                    parameters[
                        "formal_arguments"
                    ],
                )

                self.assertIn(
                    "a",
                    parameters[
                        "formal_arguments"
                    ],
                )

    def test_python_input_part_executes(
        self,
    ):
        result = make_ragged_result()

        generator = UniversalCodeGenerator(
            result.format,
            _Config(),
            TOML_ROOT / "python.toml",
        )

        parameters = (
            generator.generate_parameters()
        )

        # input_part is a template fragment. The
        # template supplies indentation to its first
        # line, while subsequent lines already contain
        # the configured base indentation.
        input_part = (
            "    "
            + parameters["input_part"]
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
                input_part,
                (
                    "    print(json.dumps("
                    "[N, L, a]))"
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
                "3\n"
                "2 10 20\n"
                "1 30\n"
                "3 40 50 60\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        self.assertEqual(
            [
                3,
                [2, 1, 3],
                [
                    [10, 20],
                    [30],
                    [40, 50, 60],
                ],
            ],
            json.loads(
                completed.stdout
            ),
        )

    def test_custom_toml_without_contract_fails_closed(
        self,
    ):
        result = make_ragged_result()

        custom_path = (
            ROOT
            / "tests"
            / "resources"
            / "test_config"
            / "test_custom_codegen_toml"
            / "nim_custom.toml"
        )

        generator = UniversalCodeGenerator(
            result.format,
            _Config(),
            custom_path,
        )

        with self.assertRaises(
            RaggedCodegenContractNotFoundError
        ):
            generator.generate_parameters()


if __name__ == "__main__":
    unittest.main()
