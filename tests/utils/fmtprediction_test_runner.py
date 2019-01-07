import os
from typing import Optional

from atcodertools.fmtprediction.predict_format import MultiplePredictionResultsError, \
    NoPredictionResultError, predict_format
from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult


class Response:

    def __init__(self, result: Optional[FormatPredictionResult], status):
        self.status = status
        if result:
            self.original_result = result
            self.simple_format = result.format
            var_info = [(var.name, var.type)
                        for var in result.format.all_vars()]
            self.types = [(name, type.to_py_type()) for name, type in var_info]


FORMAT_FILE_NAME = "format.txt"


class FormatPredictionTestRunner:

    def __init__(self, test_dir):
        self.test_dir = test_dir

    def is_valid_case(self, case_name):
        return os.path.isdir(self._get_test_case_dir(case_name))

    def load_problem_content(self, case_name: str) -> ProblemContent:
        case_dir = self._get_test_case_dir(case_name)
        format_file = os.path.join(case_dir, FORMAT_FILE_NAME)
        example_files = [os.path.join(case_dir, file)
                         for file in os.listdir(case_dir) if file != FORMAT_FILE_NAME]

        with open(format_file, 'r', encoding="utf-8") as f:
            input_format = f.read()

        examples = []
        for ex_file in example_files:
            with open(ex_file, 'r', encoding="utf-8") as f:
                examples.append(Sample(f.read(), None))

        return ProblemContent(input_format, examples)

    def run(self, case_name: str) -> Response:
        content = self.load_problem_content(case_name)

        try:
            result = predict_format(content)
            return Response(result, "OK")
        except MultiplePredictionResultsError:
            return Response(None, "Multiple results")
        except NoPredictionResultError:
            return Response(None, "No result")

    def _get_test_case_dir(self, case_name):
        return os.path.join(self.test_dir, case_name)
