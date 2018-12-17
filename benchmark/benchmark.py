# Run download_testcases.py first to generate 'test_data' directory

import os

from core.FormatPredictor import FormatPredictor, NoPredictionResultError, MultiplePredictionResultsError
from core.models.ProblemContent import ProblemContent
from core.models.Sample import Sample

FORMAT_FILE_NAME = "format.txt"

TEST_DATA_DIR = './test_data/'

predictor = FormatPredictor()


def get_test_case_dir(case_name):
    return os.path.join(TEST_DATA_DIR, case_name)


class Response:
    def __init__(self, result, status):
        self.status = status
        if result:
            self.simple_format = result.simple_format
            self.types = [(k, v.type) for k, v in result.var_to_info.items()]


def run(case_name):
    case_dir = get_test_case_dir(case_name)
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
        result = predictor.predict(problem_content)
        return Response(result, "OK")
    except MultiplePredictionResultsError as e:
        return Response(None, "Multiple results")
    except NoPredictionResultError as e:
        return Response(None, "No result")


if __name__ == "__main__":
    case_names = sorted([cand for cand in os.listdir(TEST_DATA_DIR) if os.path.isdir(get_test_case_dir(cand))])
    for case in case_names:
        response = run(case)
        if response.status == "OK":
            print("{:40}".format(case), "{:20}".format(response.status), response.simple_format, response.types)
        else:
            print("{:40}".format(case), response.status)
