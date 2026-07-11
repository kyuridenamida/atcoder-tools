import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import toml

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
    get_builtin_code_generator_info_toml_path,
)
from atcodertools.codegen.code_style_config import (
    CodeStyleConfig,
)
from atcodertools.codegen.models.code_gen_args import (
    CodeGenArgs,
)
from atcodertools.common.language import (
    ALL_LANGUAGES,
    PYTHON,
)
from atcodertools.constprediction.models.problem_constant_set import (
    ProblemConstantSet,
)
from atcodertools.fmtprediction.models.format import (
    Format,
    RepeatedCaseFormat,
    SingularPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)


def make_multi_case_content(
    case_format="X Y\n",
    sample_input=(
        "3\n"
        "1 alpha\n"
        "2 beta\n"
        "3 gamma\n"
    ),
):
    return ProblemContent(
        input_format_text="Q\n",
        input_format_blocks=[
            "Q\n",
            case_format,
        ],
        input_format_context_text=(
            "Then, Q test cases follow. "
            "Each test case has the following format."
        ),
        samples=[
            Sample(
                sample_input,
                "",
            )
        ],
    )


class TestMultiCasePredictionBridge(unittest.TestCase):
    def test_predict_format_returns_compatible_repeated_format(
        self,
    ):
        result = predict_format(
            make_multi_case_content()
        )

        self.assertIsInstance(
            result.format,
            Format,
        )
        self.assertIsInstance(
            result.format,
            RepeatedCaseFormat,
        )
        self.assertEqual(
            "Q",
            result.format.case_count_var,
        )
        self.assertEqual(
            ["Q"],
            [
                variable.name
                for variable
                in result.format.prefix_format.all_vars()
            ],
        )
        self.assertEqual(
            ["X", "Y"],
            [
                variable.name
                for variable
                in result.format.case_format.all_vars()
            ],
        )

    def test_single_case_result_remains_ordinary_format(
        self,
    ):
        content = ProblemContent(
            input_format_text="X Y\n",
            samples=[
                Sample(
                    "1 alpha\n",
                    "",
                )
            ],
        )

        result = predict_format(content)

        self.assertIsInstance(
            result.format,
            Format,
        )
        self.assertNotIsInstance(
            result.format,
            RepeatedCaseFormat,
        )


class TestMultiCaseUniversalCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.prediction_result = predict_format(
            make_multi_case_content()
        )

    def _generator_and_parameters(self, language):
        config = CodeStyleConfig(
            lang=language.name
        )
        toml_path = (
            get_builtin_code_generator_info_toml_path(
                language.name
            )
        )
        generator = UniversalCodeGenerator(
            self.prediction_result.format,
            config,
            toml_path,
        )

        return (
            generator,
            generator.generate_parameters(),
            toml.load(toml_path),
            config,
        )

    def test_all_builtin_languages_generate_loop_and_solve_call(
        self,
    ):
        for language in ALL_LANGUAGES:
            with self.subTest(language=language.name):
                (
                    generator,
                    parameters,
                    info,
                    config,
                ) = self._generator_and_parameters(
                    language
                )

                self.assertTrue(
                    parameters["prediction_success"]
                )
                self.assertTrue(
                    parameters["multi_case"]
                )
                self.assertEqual(
                    "Q",
                    parameters["case_count_var"],
                )
                self.assertEqual(
                    "X, Y",
                    parameters["actual_arguments"],
                )
                self.assertNotIn(
                    "Q",
                    parameters["formal_arguments"],
                )

                loop_header = info["loop"][
                    "header"
                ].format(
                    loop_var=parameters[
                        "case_loop_var"
                    ],
                    length="Q",
                )
                solve_call = info[
                    "solve_function"
                ].format(
                    actual_arguments="X, Y",
                )

                combined = parameters[
                    "input_part_with_solve_function"
                ]

                self.assertIn(
                    loop_header,
                    combined,
                )
                self.assertIn(
                    solve_call,
                    combined,
                )
                self.assertLess(
                    combined.index(loop_header),
                    combined.index(solve_call),
                )

                generated = (
                    language.default_code_generator(
                        CodeGenArgs(
                            template=(
                                "{{ "
                                "input_part_with_solve_function"
                                " }}"
                            ),
                            format_=(
                                self.prediction_result.format
                            ),
                            constants=ProblemConstantSet(),
                            config=config,
                        )
                    )
                )

                self.assertIn(
                    loop_header,
                    generated,
                )
                self.assertIn(
                    solve_call,
                    generated,
                )

    def test_case_loop_variable_avoids_input_collision(
        self,
    ):
        # Construct the typed format directly. The input-format tokenizer
        # intentionally splits consecutive alphabetic characters, so a
        # source-format string such as "case_index" is not suitable for
        # testing the generator's independent name-collision guard.
        prefix_format = Format()
        prefix_format.push_back(
            SingularPattern(
                Variable(
                    "Q",
                    None,
                    None,
                    Type.int,
                )
            )
        )

        case_format = Format()
        case_format.push_back(
            SingularPattern(
                Variable(
                    "case_index",
                    None,
                    None,
                    Type.int,
                )
            )
        )

        repeated_format = RepeatedCaseFormat(
            prefix_format,
            case_format,
            "Q",
        )

        generator = UniversalCodeGenerator(
            repeated_format,
            CodeStyleConfig(lang="python"),
            get_builtin_code_generator_info_toml_path(
                "python"
            ),
        )

        parameters = generator.generate_parameters()

        self.assertEqual(
            "_case_index",
            parameters["case_loop_var"],
        )
        self.assertEqual(
            "case_index",
            parameters["actual_arguments"],
        )

    def test_single_case_combined_parameter_calls_solve_once(
        self,
    ):
        result = predict_format(
            ProblemContent(
                input_format_text="X Y\n",
                samples=[
                    Sample(
                        "1 alpha\n",
                        "",
                    )
                ],
            )
        )

        path = (
            get_builtin_code_generator_info_toml_path(
                "python"
            )
        )
        generator = UniversalCodeGenerator(
            result.format,
            CodeStyleConfig(lang="python"),
            path,
        )

        combined = generator.generate_parameters()[
            "input_part_with_solve_function"
        ]

        self.assertIn(
            "X = int(next(tokens))",
            combined,
        )
        self.assertIn(
            "Y = next(tokens)",
            combined,
        )
        self.assertEqual(
            1,
            combined.count("solve(X, Y)"),
        )

    def test_all_default_templates_route_multi_case(
        self,
    ):
        for language in ALL_LANGUAGES:
            with self.subTest(
                language=language.name
            ):
                template = Path(
                    language.default_template_path
                ).read_text(
                    encoding="utf-8"
                )

                self.assertIn(
                    "input_part_with_solve_function",
                    template,
                )
                self.assertIn(
                    "multi_case",
                    template,
                )

                config = CodeStyleConfig(
                    lang=language.name
                )

                toml_path = (
                    get_builtin_code_generator_info_toml_path(
                        language.name
                    )
                )

                generator = UniversalCodeGenerator(
                    self.prediction_result.format,
                    config,
                    toml_path,
                )

                parameters = (
                    generator.generate_parameters()
                )
                info = toml.load(toml_path)

                code = (
                    language.default_code_generator(
                        CodeGenArgs(
                            template=template,
                            format_=(
                                self.prediction_result.format
                            ),
                            constants=ProblemConstantSet(),
                            config=config,
                        )
                    )
                )

                loop_header = info["loop"][
                    "header"
                ].format(
                    loop_var=parameters[
                        "case_loop_var"
                    ],
                    length="Q",
                )

                solve_call = info[
                    "solve_function"
                ].format(
                    actual_arguments="X, Y",
                )

                self.assertIn(
                    loop_header,
                    code,
                )
                self.assertEqual(
                    1,
                    code.count(solve_call),
                )

    def test_default_python_template_executes_multi_case(
        self,
    ):
        template = Path(
            PYTHON.default_template_path
        ).read_text(
            encoding="utf-8"
        )

        code = PYTHON.default_code_generator(
            CodeGenArgs(
                template=template,
                format_=self.prediction_result.format,
                constants=ProblemConstantSet(),
                config=CodeStyleConfig(
                    lang=PYTHON.name
                ),
            )
        )

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(
                directory,
                "main.py",
            )

            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(code)

            result = subprocess.run(
                [
                    sys.executable,
                    path,
                ],
                input=(
                    "3\n"
                    "1 alpha\n"
                    "2 beta\n"
                    "3 gamma\n"
                ),
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                0,
                result.returncode,
                result.stderr,
            )

    def test_generated_python_executes_all_cases(
        self,
    ):
        template = """#!/usr/bin/env python3
import sys


def solve(X: int, Y: str):
    print("{}:{}".format(X, Y))


def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word

    tokens = iterate_tokens()
    {{ input_part_with_solve_function }}


if __name__ == "__main__":
    main()
"""

        config = CodeStyleConfig(
            lang=PYTHON.name
        )

        code = PYTHON.default_code_generator(
            CodeGenArgs(
                template=template,
                format_=self.prediction_result.format,
                constants=ProblemConstantSet(),
                config=config,
            )
        )

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(
                directory,
                "main.py",
            )

            with open(path, "w") as file:
                file.write(code)

            compile_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    path,
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                0,
                compile_result.returncode,
                compile_result.stderr,
            )

            run_result = subprocess.run(
                [
                    sys.executable,
                    path,
                ],
                input=(
                    "3\n"
                    "1 alpha\n"
                    "2 beta\n"
                    "3 gamma\n"
                ),
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                0,
                run_result.returncode,
                run_result.stderr,
            )
            self.assertEqual(
                (
                    "1:alpha\n"
                    "2:beta\n"
                    "3:gamma\n"
                ),
                run_result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
