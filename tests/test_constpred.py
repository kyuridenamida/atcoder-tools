import logging
import os
import tempfile
import unittest

from atcodertools.constprediction.constants_prediction import predict_constants
from tests.utils.gzip_controller import make_html_data_controller

ANSWER_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    './resources/test_constpred/answer.txt')

fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)


def _to_str(x):
    if x is None:
        return ""
    return str(x)


class TestConstantsPrediction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.html_data_controller = make_html_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.html_data_controller.create_dir()

    def tearDown(self):
        self.html_data_controller.remove_dir()

    def test_predict_constants(self):
        with open(ANSWER_FILE, 'r') as f:
            answers = f.read().split("\n")

        agc_html_paths = [path for path in sorted(
            os.listdir(self.test_dir)) if "agc" in path]
        for html_path, answer_line in zip(agc_html_paths, answers):
            logging.debug("Testing {}".format(html_path))
            constants = predict_constants(self._load(html_path))
            output_line = "{:40} [mod]{:10} [yes]{:10} [no]{:10}".format(html_path.split(".")[0],
                                                                         _to_str(
                                                                             constants.mod),
                                                                         _to_str(
                                                                             constants.yes_str),
                                                                         _to_str(constants.no_str))
            self.assertEqual(answer_line.rstrip(), output_line.rstrip())

    def _load(self, html_path):
        with open(os.path.join(self.test_dir, html_path), 'r') as f:
            return f.read()


if __name__ == '__main__':
    unittest.main()
