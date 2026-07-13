import tempfile
import unittest
from pathlib import Path

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from tests.utils.fmtprediction_test_runner import (
    FormatPredictionTestRunner,
)
from tests.utils.problem_content_fixture import (
    read_problem_content_fixture,
    read_problem_content_payload,
    write_problem_content_fixture,
)


RESOURCE_ROOT = (
    Path(__file__).resolve().parent
    / "resources"
    / "test_fmtprediction"
)
MODERN_CORPUS_DIR = (
    RESOURCE_ROOT / "modern_multi_case"
)


class TestProblemContentFixture(unittest.TestCase):

    def test_round_trip_preserves_layout_metadata(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = (
                Path(directory) / "round-trip"
            )

            original = ProblemContent(
                input_format_text="T\n",
                input_format_blocks=[
                    "T\n",
                    "N\nA_1 ... A_N\n",
                ],
                input_format_context_text=(
                    "T test cases follow."
                ),
                samples=[
                    Sample(
                        "2\n1\n3\n2\n4 5\n",
                        "",
                    )
                ],
            )

            write_problem_content_fixture(
                case_dir,
                original,
                source={
                    "contest_id": "fixture",
                },
            )

            restored = (
                read_problem_content_fixture(
                    case_dir
                )
            )

            self.assertEqual(
                original.input_format_text,
                restored.input_format_text,
            )
            self.assertEqual(
                original.get_input_format_blocks(),
                restored.get_input_format_blocks(),
            )
            self.assertEqual(
                original.input_format_context_text,
                restored.input_format_context_text,
            )
            self.assertEqual(
                [
                    sample.get_input()
                    for sample in original.samples
                ],
                [
                    sample.get_input()
                    for sample in restored.samples
                ],
            )

    def test_legacy_fixture_fallback(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)

            (
                case_dir / "format.txt"
            ).write_text(
                "N\nA_1 ... A_N\n",
                encoding="utf-8",
            )
            (
                case_dir / "ex_2.txt"
            ).write_text(
                "2\n4 5\n",
                encoding="utf-8",
            )
            (
                case_dir / "ex_1.txt"
            ).write_text(
                "1\n3\n",
                encoding="utf-8",
            )

            restored = (
                read_problem_content_fixture(
                    case_dir
                )
            )

            self.assertEqual(
                "N\nA_1 ... A_N\n",
                restored.input_format_text,
            )
            self.assertEqual(
                [
                    "1\n3\n",
                    "2\n4 5\n",
                ],
                [
                    sample.get_input()
                    for sample in restored.samples
                ],
            )

    def test_modern_real_corpus_exercises_multi_case(
        self,
    ):
        runner = FormatPredictionTestRunner(
            str(MODERN_CORPUS_DIR)
        )

        case_names = sorted(
            path.name
            for path in MODERN_CORPUS_DIR.iterdir()
            if runner.is_valid_case(
                path.name
            )
        )

        self.assertEqual(
            [
                "abc354-f",
                "arc185-a",
                "arc222-f",
            ],
            case_names,
        )

        for case_name in case_names:
            with self.subTest(
                case_name=case_name
            ):
                case_dir = (
                    MODERN_CORPUS_DIR
                    / case_name
                )
                payload = (
                    read_problem_content_payload(
                        case_dir
                    )
                )
                response = runner.run(case_name)

                self.assertEqual(
                    "OK",
                    response.status,
                )
                self.assertEqual(
                    "RepeatedCaseFormat",
                    type(
                        response.simple_format
                    ).__name__,
                )
                self.assertEqual(
                    payload["source"][
                        "expected_case_count_var"
                    ],
                    response.simple_format.case_count_var,
                )
                self.assertGreaterEqual(
                    len(
                        payload[
                            "input_format_blocks"
                        ]
                    ),
                    2,
                )
                self.assertTrue(
                    payload[
                        "input_format_context_text"
                    ].strip()
                )


if __name__ == "__main__":
    unittest.main()
