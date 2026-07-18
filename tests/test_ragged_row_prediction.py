import shutil
import tempfile
import unittest
from pathlib import Path

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import (
    Sample,
)
from atcodertools.fmtprediction.models.type import (
    Type,
)
from atcodertools.fmtprediction.ragged_row import (
    NoRaggedRowPredictionError,
    detect_same_line_ragged_row_schemas,
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


class TestSameLineRaggedRowSynthetic(
    unittest.TestCase
):
    def test_detects_length_field_at_nonzero_position(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "n m d\n"
                "c_1 s_1 k_1 "
                "a_{1,1} ... a_{1,k_1}\n"
                "...\n"
                "c_m s_m k_m "
                "a_{m,1} ... a_{m,k_m}\n"
            ),
            samples=[
                Sample(
                    (
                        "3 2 1\n"
                        "10 20 2 1 2\n"
                        "30 40 1 5\n"
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

        self.assertEqual(
            "m",
            prediction.schema.row_count_var,
        )

        self.assertEqual(
            ("c", "s", "k"),
            prediction.schema.prefix_fields,
        )

        self.assertEqual(
            2,
            prediction.schema.length_field_position,
        )

        self.assertEqual(
            "a",
            prediction.schema.values_name,
        )

        self.assertEqual(
            (2,),
            prediction.sample_row_counts,
        )

    def test_accepts_consecutive_explicit_value_prefix(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N\n"
                "L_1 A_{1,1} A_{1,2} "
                "\\ldots A_{1,L_1}\n"
                "L_2 A_{2,1} A_{2,2} "
                "\\ldots A_{2,L_2}\n"
                "\\vdots\n"
                "L_N A_{N,1} A_{N,2} "
                "\\ldots A_{N,L_N}\n"
                "X Y\n"
            ),
            samples=[
                Sample(
                    (
                        "3\n"
                        "3 10 20 30\n"
                        "1 7\n"
                        "4 5 6 7 8\n"
                        "3 4\n"
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

        self.assertEqual(
            "N",
            prediction.schema.row_count_var,
        )
        self.assertEqual(
            ("L",),
            prediction.schema.prefix_fields,
        )
        self.assertEqual(
            0,
            prediction.schema.length_field_position,
        )
        self.assertEqual(
            "A",
            prediction.schema.values_name,
        )
        self.assertEqual(
            1,
            prediction.schema.value_start_index,
        )
        self.assertEqual(
            ["X", "Y"],
            [
                variable.name
                for variable
                in prediction.suffix_format.all_vars()
            ],
        )

    def test_rejects_nonconsecutive_explicit_value_prefix(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N\n"
                "L_1 A_{1,1} A_{1,3} "
                "\\ldots A_{1,L_1}\n"
                "\\vdots\n"
                "L_N A_{N,1} A_{N,3} "
                "\\ldots A_{N,L_N}\n"
            ),
            samples=[
                Sample(
                    (
                        "2\n"
                        "3 10 20 30\n"
                        "3 40 50 60\n"
                    ),
                    "",
                ),
            ],
        )

        self.assertEqual(
            [],
            detect_same_line_ragged_row_schemas(
                content
            ),
        )

        with self.assertRaises(
            NoRaggedRowPredictionError
        ):
            predict_same_line_ragged_rows(
                content
            )

    def test_rejects_explicit_value_prefix_starting_at_two(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N\n"
                "L_1 A_{1,2} "
                "\\ldots A_{1,L_1}\n"
                "\\vdots\n"
                "L_N A_{N,2} "
                "\\ldots A_{N,L_N}\n"
            ),
            samples=[
                Sample(
                    (
                        "2\n"
                        "3 10 20 30\n"
                        "3 40 50 60\n"
                    ),
                    "",
                ),
            ],
        )

        self.assertEqual(
            [],
            detect_same_line_ragged_row_schemas(
                content
            ),
        )

        with self.assertRaises(
            NoRaggedRowPredictionError
        ):
            predict_same_line_ragged_rows(
                content
            )

    def test_rejects_rectangular_array(
        self,
    ):
        content = ProblemContent(
            input_format_text=(
                "N M\n"
                "A_{1,1} ... A_{1,M}\n"
                "...\n"
                "A_{N,1} ... A_{N,M}\n"
            ),
            samples=[
                Sample(
                    (
                        "2 3\n"
                        "1 2 3\n"
                        "4 5 6\n"
                    ),
                    "",
                ),
            ],
        )

        self.assertEqual(
            [],
            detect_same_line_ragged_row_schemas(
                content
            ),
        )

        with self.assertRaises(
            NoRaggedRowPredictionError
        ):
            predict_same_line_ragged_rows(
                content
            )

    def test_rejects_two_line_length_prefix(
        self,
    ):
        content = ProblemContent(
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
                        "3 2\n"
                        "2\n"
                        "1 3\n"
                        "1\n"
                        "2\n"
                    ),
                    "",
                ),
            ],
        )

        with self.assertRaises(
            NoRaggedRowPredictionError
        ):
            predict_same_line_ragged_rows(
                content
            )


class TestSameLineRaggedRowOfficialCases(
    unittest.TestCase
):
    EXPECTED = {
        "abc271b": (
            "N",
            ("L",),
            0,
            "a",
        ),
        "abc315e": (
            "N",
            ("C",),
            0,
            "P",
        ),
        "abc404d": (
            "M",
            ("K",),
            0,
            "A",
        ),
        "arc056d": (
            "N",
            ("M",),
            0,
            "t",
        ),
        "hokudaihitachi2018a": (
            "K",
            ("d", "c"),
            0,
            "v",
        ),
        "nadafes2022day1j": (
            "Q",
            ("K",),
            0,
            "p",
        ),
        "utpc2012j": (
            "m",
            ("c", "s", "k"),
            2,
            "a",
        ),
    }

    @classmethod
    def setUpClass(cls):
        cls.temporary_root = Path(
            tempfile.mkdtemp(
                prefix=(
                    "atcoder_tools_ragged_"
                    "official_test_"
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

    def test_all_seven_official_cases(
        self,
    ):
        self.assertEqual(
            7,
            len(self.EXPECTED),
        )

        for normalized_id, expected in (
            self.EXPECTED.items()
        ):
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

                (
                    row_count_var,
                    prefix_fields,
                    length_position,
                    values_name,
                ) = expected

                self.assertEqual(
                    row_count_var,
                    prediction.schema.row_count_var,
                )

                self.assertEqual(
                    prefix_fields,
                    prediction.schema.prefix_fields,
                )

                self.assertEqual(
                    length_position,
                    (
                        prediction.schema
                        .length_field_position
                    ),
                )

                self.assertEqual(
                    values_name,
                    prediction.schema.values_name,
                )

                length_name = (
                    prefix_fields[
                        length_position
                    ]
                )

                self.assertEqual(
                    Type.int,
                    prediction.var_to_type[
                        length_name
                    ],
                )

                self.assertEqual(
                    Type.int,
                    prediction.var_to_type[
                        values_name
                    ],
                )

                self.assertEqual(
                    len(content.get_samples()),
                    len(
                        prediction.sample_row_counts
                    ),
                )

    def test_abc166_b_remains_two_line_followup(
        self,
    ):
        case_name = self.available.get(
            "abc166b"
        )

        self.assertIsNotNone(case_name)

        content = (
            self.runner.load_problem_content(
                case_name
            )
        )

        with self.assertRaises(
            NoRaggedRowPredictionError
        ):
            predict_same_line_ragged_rows(
                content
            )


if __name__ == "__main__":
    unittest.main()
