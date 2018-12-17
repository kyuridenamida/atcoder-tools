import shutil
import tarfile
import tempfile
import unittest
import os

from core.FormatPredictor import FormatPredictor, NoPredictionResultError, MultiplePredictionResultsError
from core.models.ProblemContent import ProblemContent
from core.models.Sample import Sample

FORMAT_FILE_NAME = "format.txt"
ANSWER_FILE = "./resources/TestFormatPredictor/answer.txt"
TEST_DATA_GZIP_FILE = './resources/TestFormatPredictor/test_data.tar.gz'

predictor = FormatPredictor()


class Response:
    def __init__(self, result, status):
        self.status = status
        if result:
            self.simple_format = result.simple_format
            self.types = [(k, v.type) for k, v in result.var_to_info.items()]


class TestFormatPredictor(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.mkdtemp()
        tf = tarfile.open(TEST_DATA_GZIP_FILE, 'r')
        tf.extractall(temp_dir)
        self.test_dir = os.path.join(temp_dir, "test_data")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_predict(self):
        case_names = sorted(
            [cand for cand in os.listdir(self.test_dir) if os.path.isdir(self._get_test_case_dir(cand))])
        output_text = ""
        for case in case_names:
            response = self._run(case)
            if response.status == "OK":
                output_text += "{:40} {:20} {} {}\n".format(case, response.status, response.simple_format,
                                                            response.types)
            else:
                output_text += "{:40} {}\n".format(case, response.status)

        with open(ANSWER_FILE, 'r') as f:
            answer = f.read()
        self.assertEqual(answer, output_text)

    def _get_test_case_dir(self, case_name):
        return os.path.join(self.test_dir, case_name)

    def _run(self, case_name):
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
            result = predictor.predict(problem_content)
            return Response(result, "OK")
        except MultiplePredictionResultsError as e:
            return Response(None, "Multiple results")
        except NoPredictionResultError as e:
            return Response(None, "No result")


if __name__ == "__main__":
    unittest.main()
