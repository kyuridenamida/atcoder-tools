import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


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


EXPECTED_SOLVE_FUNCTIONS = {'cpp': 'solve({actual_arguments});',
                            'cs': 'new Program().Solve({actual_arguments});',
                            'd': 'solve({actual_arguments});',
                            'go': 'solve({actual_arguments})',
                            'java': 'solve({actual_arguments});',
                            'julia': 'solve({actual_arguments})',
                            'nim': 'solve({actual_arguments})',
                            'python': 'solve({actual_arguments})',
                            'rust': 'solve({actual_arguments});',
                            'swift': '_ = solve({actual_arguments})'}


class TestMultiCaseUniversalCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.prediction_result = predict_format(
            make_multi_case_content()
        )

    def _generator_and_parameters(self, language):
        config = CodeStyleConfig(
            lang=language.name
        )
        generator = UniversalCodeGenerator(
            self.prediction_result.format,
            config,
            get_builtin_code_generator_info_toml_path(
                language.name
            ),
        )

        return (
            generator,
            generator.generate_parameters(),
            generator.info,
            config,
        )

    def test_all_builtin_languages_expose_material_contract(
        self,
    ):
        self.assertEqual(10, len(ALL_LANGUAGES))

        for language in ALL_LANGUAGES:
            with self.subTest(language=language.name):
                (
                    _,
                    parameters,
                    information,
                    _,
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

                for name in (
                    "prefix_input_part",
                    "case_input_part",
                    "case_count_var",
                    "case_loop_var",
                    "multi_case",
                ):
                    self.assertIn(
                        name,
                        parameters,
                    )

                self.assertNotIn(
                    "input_part_with_solve_function",
                    parameters,
                )
                self.assertNotIn(
                    "input_part_with_solve_function_nested",
                    parameters,
                )
                self.assertNotIn(
                    "solve_function",
                    information,
                )

                if language.name == "d":
                    self.assertFalse(
                        parameters[
                            "case_input_part"
                        ].startswith("\n")
                    )

    def test_case_loop_variable_avoids_input_collision(
        self,
    ):
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

    def test_single_case_parameters_remain_material_only(
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

        generator = UniversalCodeGenerator(
            result.format,
            CodeStyleConfig(lang="python"),
            get_builtin_code_generator_info_toml_path(
                "python"
            ),
        )
        parameters = generator.generate_parameters()

        self.assertFalse(
            parameters["multi_case"]
        )
        self.assertIn(
            "X = int(next(tokens))",
            parameters["input_part"],
        )
        self.assertIn(
            "Y = next(tokens)",
            parameters["input_part"],
        )
        self.assertNotIn(
            "input_part_with_solve_function",
            parameters,
        )

    def test_all_default_templates_route_multi_case(
        self,
    ):
        for language in ALL_LANGUAGES:
            with self.subTest(language=language.name):
                template = Path(
                    language.default_template_path
                ).read_text(
                    encoding="utf-8"
                )

                for name in (
                    "multi_case",
                    "prefix_input_part",
                    "case_input_part",
                    "case_count_var",
                    "case_loop_var",
                ):
                    self.assertIn(
                        name,
                        template,
                    )

                self.assertNotIn(
                    "input_part_with_solve_function",
                    template,
                )

                (
                    _,
                    parameters,
                    information,
                    config,
                ) = self._generator_and_parameters(
                    language
                )

                code = language.default_code_generator(
                    CodeGenArgs(
                        template=template,
                        format_=(
                            self.prediction_result.format
                        ),
                        constants=ProblemConstantSet(),
                        config=config,
                    )
                )

                loop_header = information[
                    "loop"
                ]["header"].format(
                    loop_var=parameters[
                        "case_loop_var"
                    ],
                    length="Q",
                )
                solve_call = (
                    EXPECTED_SOLVE_FUNCTIONS[
                        language.name
                    ].format(
                        actual_arguments="X, Y"
                    )
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
        template = r"""#!/usr/bin/env python3
import sys

def solve(X: int, Y: str):
    print("{}:{}".format(X, Y))

def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    {% if prediction_success %}
    {% if multi_case %}
    {{ prefix_input_part }}
    for {{ case_loop_var }} in range({{ case_count_var }}):
        {{ case_input_part | replace('\n', '\n' ~ "    ") }}
        solve({{ actual_arguments }})
    {% else %}
    {{ input_part }}
    solve({{ actual_arguments }})
    {% endif %}
    {% endif %}

if __name__ == "__main__":
    main()
"""

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

    def test_old_custom_template_fails_explicitly_for_multi_case(
        self,
    ):
        template = """{% if prediction_success %}
{{ input_part }}
{% else %}
FAILED_TO_PREDICT
{% endif %}
"""

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

        self.assertIn(
            "FAILED_TO_PREDICT",
            code,
        )
        self.assertNotIn(
            "X = int(next(tokens))",
            code,
        )

    def test_single_case_custom_template_remains_supported(
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

        template = """{% if prediction_success %}
{{ input_part }}
{% else %}
FAILED_TO_PREDICT
{% endif %}
"""

        code = PYTHON.default_code_generator(
            CodeGenArgs(
                template=template,
                format_=result.format,
                constants=ProblemConstantSet(),
                config=CodeStyleConfig(
                    lang=PYTHON.name
                ),
            )
        )

        self.assertIn(
            "X = int(next(tokens))",
            code,
        )
        self.assertNotIn(
            "FAILED_TO_PREDICT",
            code,
        )


if __name__ == "__main__":
    unittest.main()
