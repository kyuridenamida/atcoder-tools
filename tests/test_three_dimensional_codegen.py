import os
import subprocess
import sys
import tempfile
import unittest

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
    get_builtin_code_generator_info_toml_path,
)
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.common.language import PYTHON
from atcodertools.constprediction.models.problem_constant_set import (
    ProblemConstantSet,
)
from atcodertools.fmtprediction.models.format import (
    Format,
    SingularPattern,
    ThreeDimensionalPattern,
)
from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


def make_index(maximum):
    index = Index()
    index.update("1")
    index.update(maximum)
    return index


def make_three_dimensional_format():
    format_ = Format()

    for name in ("D", "H", "W"):
        format_.push_back(
            SingularPattern(
                Variable(
                    name,
                    None,
                    None,
                    Type.int,
                )
            )
        )

    array = Variable(
        "A",
        make_index("D"),
        make_index("H"),
        Type.int,
        third_index=make_index("W"),
    )

    format_.push_back(
        ThreeDimensionalPattern(array)
    )

    return format_


class TestThreeDimensionalCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.format = make_three_dimensional_format()
        self.config = CodeStyleConfig(
            lang=PYTHON.name
        )
        self.toml_path = (
            get_builtin_code_generator_info_toml_path(
                PYTHON.name
            )
        )

    def generate_parameters(self):
        generator = UniversalCodeGenerator(
            self.format,
            self.config,
            self.toml_path,
        )

        return generator.generate_parameters()

    def test_three_dimensional_parameters(self):
        parameters = self.generate_parameters()

        self.assertEqual(
            "D, H, W, A",
            parameters["actual_arguments"],
        )
        self.assertIn(
            'A: "List[List[List[int]]]"',
            parameters["formal_arguments"],
        )

        combined = parameters[
            "input_part_with_solve_function"
        ]

        self.assertIn(
            "range(D)",
            combined,
        )
        self.assertIn(
            "range(H)",
            combined,
        )
        self.assertIn(
            "range(W)",
            combined,
        )
        self.assertIn(
            "solve(D, H, W, A)",
            combined,
        )

    def test_generated_python_executes(self):
        template = "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "",
                (
                    'def solve(D: int, H: int, W: int, '
                    'A: "List[List[List[int]]]"):'
                ),
                (
                    "    print("
                    "D, H, W, A[1][0][2], "
                    "sum("
                    "value "
                    "for plane in A "
                    "for row in plane "
                    "for value in row"
                    ")"
                    ")"
                ),
                "",
                "def main():",
                "    def iterate_tokens():",
                "        for line in sys.stdin:",
                "            for word in line.split():",
                "                yield word",
                "",
                "    tokens = iterate_tokens()",
                "    {{ input_part_with_solve_function }}",
                "",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        )

        code = PYTHON.default_code_generator(
            CodeGenArgs(
                template=template,
                format_=self.format,
                constants=ProblemConstantSet(),
                config=self.config,
            )
        )

        sample_input = (
            "2 2 3\n"
            "1 2 3\n"
            "4 5 6\n"
            "7 8 9\n"
            "10 11 12\n"
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
                input=sample_input,
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                0,
                run_result.returncode,
                run_result.stderr,
            )
            self.assertEqual(
                "2 2 3 9 78\n",
                run_result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
