import tempfile
import unittest
import os
from logging import getLogger, Formatter, StreamHandler, DEBUG

from tests.utils.gzip_controller import make_tst_data_controller
from tests.utils.fmtprediction_test_runner import FormatPredictionTestRunner

ANSWER_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    './resources/test_fmtprediction/answer.txt')

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler()
formatter = Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TestFormatPrediction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_controller = make_tst_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.test_data_controller.create_dir()

    def tearDown(self):
        self.test_data_controller.remove_dir()

    def test_overall(self):
        runner = FormatPredictionTestRunner(self.test_dir)
        case_names = sorted(
            [cand for cand in os.listdir(self.test_dir) if runner.is_valid_case(cand)])
        output_text = ""
        for case in case_names:
            response = runner.run(case)

            if response.status == "OK":
                output_text += "{:40} {:20} {} {}\n".format(case, response.status, response.simple_format,
                                                            response.types)
            else:
                output_text += "{:40} {}\n".format(case, response.status)

        with open(ANSWER_FILE, 'r') as f:
            answer = f.read()

        for ans, out in zip(answer.split("\n"), output_text.split("\n")):
            if ans != out:
                # Case name is expected to be stored to the first column in the
                # file.
                case_name = ans.split()[0]
                content = runner.load_problem_content(case_name)
                logger.debug("=== {} ===".format(case_name))
                logger.debug(
                    "Input Format:\n{}".format(content.input_format_text))
                for idx, s in enumerate(content.samples):
                    logger.debug(
                        "Sample Input {num}:\n{inp}".format(inp=s.get_input(), num=idx + 1))
                self.assertEqual(ans, out)

        self.assertEqual(len(answer), len(output_text))


if __name__ == "__main__":
    unittest.main()
