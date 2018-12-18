import os
from core.FormatPredictor import FormatPredictor, MultiplePredictionResultsError, NoPredictionResultError
from core.models.ProblemContent import ProblemContent
from core.models.Sample import Sample
from core.models.predictor.FormatPredictionResult import FormatPredictionResult


class Response:
    def __init__(self, result: FormatPredictionResult, status):
        self.status = status
        if result:
            self.original_result = result
            self.simple_format = result.simple_format
            self.types = [(k, v.type) for k, v in result.var_to_info.items()]


FORMAT_FILE_NAME = "format.txt"


class TestFormatPredictorRunner:
    def __init__(self, test_dir):
        self.test_dir = test_dir

    def is_valid_case(self, case_name):
        return os.path.isdir(self._get_test_case_dir(case_name))

    def run(self, case_name: str) -> Response:
        case_dir = self._get_test_case_dir(case_name)
        format_file = os.path.join(case_dir, FORMAT_FILE_NAME)
        example_files = [os.path.join(case_dir, file) for file in os.listdir(case_dir) if file != FORMAT_FILE_NAME]

        with open(format_file, 'r') as f:
            input_format = f.read()

        examples = []
        for ex_file in example_files:
            with open(ex_file, 'r') as f:
                examples.append(Sample(f.read(), None))
        problem_content = ProblemContent.of(input_format, examples)

        try:
            result = FormatPredictor.predict(problem_content)
            return Response(result, "OK")
        except MultiplePredictionResultsError:
            return Response(None, "Multiple results")
        except NoPredictionResultError:
            return Response(None, "No result")

    def _get_test_case_dir(self, case_name):
        return os.path.join(self.test_dir, case_name)
