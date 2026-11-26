import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.codegen.ragged_row_python_generator import (
    build_typed_ragged_row_pattern,
    generate_same_line_ragged_row_python,
)
from atcodertools.fmtprediction.models.type import (
    Type,
)
from atcodertools.fmtprediction.ragged_row import (
    predict_same_line_ragged_rows,
)
from tests.utils.fmtprediction_test_runner import (
    FormatPredictionTestRunner,
)
from tests.utils.gzip_controller import (
    make_tst_data_controller,
)


def normalize_identifier(value):
    return "".join(
        character
        for character in value.lower()
        if character.isalnum()
    )


class TestRaggedRowPythonGenerator(
    unittest.TestCase
):
    def make_prediction(self):
        content = ProblemContent(
            input_format_text=(
                "m\n"
                "c_1 s_1 k_1 "
                "a_{1,1} ... a_{1,k_1}\n"
                "...\n"
                "c_m s_m k_m "
                "a_{m,1} ... a_{m,k_m}\n"
            ),
            samples=[
                Sample(
                    (
                        "3\n"
                        "10 20 2 1 2\n"
                        "30 40 1 5\n"
                        "50 60 3 7 8 9\n"
                    ),
                    "",
                ),
            ],
        )

        return (
            predict_same_line_ragged_rows(
                content
            )
        )

    def test_builds_typed_pattern(
        self,
    ):
        prediction = self.make_prediction()

        pattern = (
            build_typed_ragged_row_pattern(
                prediction
            )
        )

        self.assertEqual(
            "m",
            pattern.row_count_var,
        )

        self.assertEqual(
            ("c", "s", "k"),
            tuple(
                field.name
                for field
                in pattern.prefix_fields
            ),
        )

        self.assertEqual(
            "k",
            pattern.length_field.name,
        )

        self.assertEqual(
            Type.int,
            pattern.length_field.type,
        )

        self.assertEqual(
            "a",
            pattern.values_field.name,
        )

    def test_generated_reader_executes(
        self,
    ):
        prediction = self.make_prediction()

        generated = (
            generate_same_line_ragged_row_python(
                prediction
            )
        )

        program = "\n".join(
            [
                "import json",
                "m = int(input())",
                generated.render(),
                (
                    "print(json.dumps("
                    "[c, s, k, a]))"
                ),
            ]
        )

        completed = subprocess.run(
            [
                "python3",
                "-c",
                program,
            ],
            input=(
                "3\n"
                "10 20 2 1 2\n"
                "30 40 1 5\n"
                "50 60 3 7 8 9\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        self.assertEqual(
            [
                [10, 30, 50],
                [20, 40, 60],
                [2, 1, 3],
                [
                    [1, 2],
                    [5],
                    [7, 8, 9],
                ],
            ],
            json.loads(
                completed.stdout
            ),
        )

        self.assertEqual(
            ("c", "s", "k", "a"),
            generated.actual_arguments,
        )

    def test_generated_reader_checks_length(
        self,
    ):
        prediction = self.make_prediction()

        generated = (
            generate_same_line_ragged_row_python(
                prediction
            )
        )

        program = "\n".join(
            [
                "m = int(input())",
                generated.render(),
            ]
        )

        completed = subprocess.run(
            [
                "python3",
                "-c",
                program,
            ],
            input=(
                "1\n"
                "10 20 3 1 2\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertNotEqual(
            0,
            completed.returncode,
        )

        self.assertIn(
            "ragged row length mismatch",
            completed.stderr,
        )


class TestRaggedRowPythonOfficialCases(
    unittest.TestCase
):
    CASE_IDS = (
        "abc271b",
        "abc315e",
        "abc404d",
        "arc056d",
        "hokudaihitachi2018a",
        "nadafes2022day1j",
        "utpc2012j",
    )

    @classmethod
    def setUpClass(cls):
        cls.temporary_root = Path(
            tempfile.mkdtemp(
                prefix=(
                    "atcoder_tools_ragged_"
                    "python_official_"
                )
            )
        )

        cls.controller = (
            make_tst_data_controller(
                str(cls.temporary_root)
            )
        )

        cls.test_dir = Path(
            cls.controller.create_dir()
        )

        cls.runner = (
            FormatPredictionTestRunner(
                str(cls.test_dir)
            )
        )

        cls.available = {
            normalize_identifier(path.name):
            path.name
            for path in cls.test_dir.iterdir()
            if path.is_dir()
        }

    @classmethod
    def tearDownClass(cls):
        try:
            cls.controller.remove_dir()
        except Exception:
            pass

        shutil.rmtree(
            cls.temporary_root,
            ignore_errors=True,
        )

    def test_all_seven_generate_python(
        self,
    ):
        self.assertEqual(
            7,
            len(self.CASE_IDS),
        )

        for normalized_id in self.CASE_IDS:
            with self.subTest(
                case_id=normalized_id
            ):
                case_name = self.available.get(
                    normalized_id
                )

                self.assertIsNotNone(
                    case_name
                )

                content = (
                    self.runner
                    .load_problem_content(
                        case_name
                    )
                )

                prediction = (
                    predict_same_line_ragged_rows(
                        content
                    )
                )

                generated = (
                    generate_same_line_ragged_row_python(
                        prediction
                    )
                )

                self.assertTrue(
                    generated.declarations
                )

                self.assertTrue(
                    generated.input_part
                )

                self.assertIn(
                    prediction.schema.values_name,
                    generated.actual_arguments,
                )

                self.assertEqual(
                    Type.int,
                    generated.pattern.length_field.type,
                )


if __name__ == "__main__":
    unittest.main()
