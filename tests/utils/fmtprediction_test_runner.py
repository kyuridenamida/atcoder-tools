import os
from typing import Optional

from atcodertools.fmtprediction.models.format_prediction_result import (
    FormatPredictionResult,
)
from atcodertools.fmtprediction.predict_format import (
    MultiplePredictionResultsError,
    NoPredictionResultError,
    predict_format,
)
from tests.utils.problem_content_fixture import (
    is_problem_content_fixture,
    read_problem_content_fixture,
)


class Response:

    def __init__(
        self,
        result: Optional[
            FormatPredictionResult
        ],
        status,
    ):
        self.status = status

        if result:
            self.original_result = result
            self.simple_format = result.format

            variable_information = [
                (
                    variable.name,
                    variable.type,
                )
                for variable
                in result.format.all_vars()
            ]

            self.types = [
                (
                    name,
                    value_type.to_py_type(),
                )
                for name, value_type
                in variable_information
            ]


class FormatPredictionTestRunner:

    def __init__(self, test_dir):
        self.test_dir = test_dir

    def is_valid_case(self, case_name):
        return is_problem_content_fixture(
            self._get_test_case_dir(
                case_name
            )
        )

    def load_problem_content(
        self,
        case_name: str,
    ):
        return read_problem_content_fixture(
            self._get_test_case_dir(
                case_name
            )
        )

    def run(self, case_name: str) -> Response:
        content = self.load_problem_content(
            case_name
        )

        try:
            result = predict_format(content)
            return Response(result, "OK")
        except MultiplePredictionResultsError:
            return Response(
                None,
                "Multiple results",
            )
        except NoPredictionResultError:
            return Response(
                None,
                "No result",
            )

    def _get_test_case_dir(self, case_name):
        return os.path.join(
            self.test_dir,
            case_name,
        )
