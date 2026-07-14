import html
import json
from pathlib import Path
import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.format import (
    RepeatedCaseFormat,
)
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)
from atcodertools.fmtprediction.predict_format import (
    NoMultiCaseFormatFoundError,
    predict_multi_case_format,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "resources"
    / "test_multi_case"
    / "official_layout_cases.json"
)


class TestOfficialMultiCaseLayouts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            FIXTURE_PATH.read_text(
                encoding="utf-8"
            )
        )

    def _content_from_case(self, case):
        evidence = case[
            "statement_evidence_text"
        ]

        original_html = None

        if evidence:
            original_html = (
                "<html><body><p>"
                + html.escape(evidence)
                + "</p></body></html>"
            )

        return ProblemContent(
            input_format_text=case[
                "input_format_text"
            ],
            input_format_blocks=case[
                "input_format_blocks"
            ],
            input_format_context_text=case[
                "input_format_context_text"
            ],
            original_html=original_html,
            samples=[
                Sample(sample_input, "")
                for sample_input
                in case["sample_inputs"]
            ],
        )

    def test_fixture_schema_and_counts(self):
        self.assertEqual(
            (
                "atcoder_tools_multi_case_"
                "official_layouts_v1"
            ),
            self.fixture["schema"],
        )

        cases = self.fixture["cases"]

        self.assertEqual(15, len(cases))
        self.assertEqual(
            9,
            sum(
                case["expected_multi"]
                for case in cases
            ),
        )
        self.assertEqual(
            6,
            sum(
                not case["expected_multi"]
                for case in cases
            ),
        )

    def test_all_normalized_official_layouts(self):
        for case in self.fixture["cases"]:
            with self.subTest(
                task_id=case["task_id"]
            ):
                content = self._content_from_case(
                    case
                )

                if case["expected_multi"]:
                    direct = (
                        predict_multi_case_format(
                            content
                        )
                    )

                    self.assertEqual(
                        case["expected_layout"],
                        direct.layout,
                    )
                    self.assertEqual(
                        case[
                            "expected_count_variable"
                        ],
                        direct.case_count_var,
                    )

                    full = predict_format(content)

                    self.assertIsInstance(
                        full.format,
                        RepeatedCaseFormat,
                    )
                else:
                    with self.assertRaises(
                        NoMultiCaseFormatFoundError
                    ):
                        predict_multi_case_format(
                            content
                        )

                    full = predict_format(content)

                    self.assertNotIsInstance(
                        full.format,
                        RepeatedCaseFormat,
                    )


if __name__ == "__main__":
    unittest.main()
