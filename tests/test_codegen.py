import sys
import tempfile
import unittest
import os

from atcodertools.codegen.code_generator import CodeGenerator
from atcodertools.codegen.java_code_generator import JavaCodeGenerator
from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from tests.utils.gzip_controller import make_test_data_controller
from tests.utils.fmtprediction_test_runner import FormatPredictionTestRunner, Response

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_codegen/")
LANGS = ["cpp", "java"]


def load_generated_code(py_test_name, lang):
    with open(os.path.join(RESOURCE_DIR, py_test_name, lang, "generated_code.txt"), 'r') as f:
        return f.read()


def load_intermediate_types(py_test_name):
    with open(os.path.join(RESOURCE_DIR, py_test_name, "intermediate_types.txt"), 'r') as f:
        return f.read()


def load_intermediate_format(py_test_name):
    with open(os.path.join(RESOURCE_DIR, py_test_name, "intermediate_format.txt"), 'r') as f:
        return f.read()


class TestCodeGenerator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_controller = make_test_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.test_data_controller.create_dir()
        self.runner = FormatPredictionTestRunner(self.test_dir)
        self.lang_to_template_file = {
            "cpp": "template.cpp",
            "java": "template.java"
        }
        self.lang_to_code_generator = {
            "cpp": CppCodeGenerator,
            "java": JavaCodeGenerator,
        }

    def tearDown(self):
        self.test_data_controller.remove_dir()

    def test_long_case(self):
        response = self.runner.run('rco-contest-2017-qual-B')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_two_dimensional_case(self):
        response = self.runner.run('kupc2012pr-D')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_float_case(self):
        response = self.runner.run('tenka1-2014-qualb-E')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def verify(self, response: Response, py_test_name: str, lang: str):
        self.assertEqual(
            load_intermediate_format(py_test_name),
            str(response.simple_format))
        self.assertEqual(
            load_intermediate_types(py_test_name),
            str(response.types))
        self.assertEqual(load_generated_code(py_test_name, lang),
                         self.get_generator(lang).generate_code(response.original_result))

    def get_generator(self, lang: str) -> CodeGenerator:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang])
        with open(template_file, 'r') as f:
            return self.lang_to_code_generator[lang](f.read())


if __name__ == "__main__":
    unittest.main()
