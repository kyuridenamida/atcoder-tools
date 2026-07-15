import json
from pathlib import Path
import unittest

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "resources"
    / "test_three_dimensional"
    / "official_cases.json"
)


class TestThreeDimensionalOfficialCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            FIXTURE_PATH.read_text(
                encoding="utf-8"
            )
        )

    def _content(self, case):
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
            original_html="",
            samples=[
                Sample(sample_input, "")
                for sample_input
                in case["sample_inputs"]
            ],
        )

    def test_fixture_schema_and_count(self):
        self.assertEqual(
            (
                "atcoder_tools_three_dimensional_"
                "official_cases_v1"
            ),
            self.fixture["schema"],
        )
        self.assertEqual(
            4,
            len(self.fixture["cases"]),
        )
        self.assertEqual(
            {
                "abc080_c",
                "abc322_d",
                "abc366_d",
                "code_festival_2015_okinawa_c",
            },
            {
                case["task_id"]
                for case in self.fixture["cases"]
            },
        )

    def test_official_prediction_contracts(self):
        for case in self.fixture["cases"]:
            with self.subTest(
                task_id=case["task_id"]
            ):
                result = predict_format(
                    self._content(case)
                )
                format_ = result.format

                variables = {
                    variable.name: variable
                    for variable in format_.all_vars()
                }

                pattern_classes = {}

                for pattern in format_.sequence:
                    for variable in pattern.all_vars():
                        pattern_classes[
                            variable.name
                        ] = type(pattern).__name__

                for name, expected in case[
                    "expected_variables"
                ].items():
                    self.assertIn(
                        name,
                        variables,
                    )
                    variable = variables[name]

                    self.assertEqual(
                        expected["type"],
                        str(variable.type),
                    )
                    self.assertEqual(
                        expected["dim_num"],
                        variable.dim_num(),
                    )

                for name, expected_class in case[
                    "expected_patterns"
                ].items():
                    self.assertEqual(
                        expected_class,
                        pattern_classes[name],
                    )


if __name__ == "__main__":
    unittest.main()
