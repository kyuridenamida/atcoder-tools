import shutil
import sys
import tempfile
import unittest
import os

from core.code_generation.CodeGenerator import CodeGenerator
from core.code_generation.JavaCodeGenerator import JavaCodeGenerator
from core.code_generation.CppCodeGenerator import CppCodeGenerator
from test.utils.TestDataUtil import TestDataUtil
from test.utils.TestFormatPredictorRunner import TestFormatPredictorRunner, Response

RESOURCE_DIR = "./resources/TestCodeGenerator/"
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
        self.test_data_util = TestDataUtil(tempfile.mkdtemp())
        self.test_dir = self.test_data_util.create_dir()
        self.runner = TestFormatPredictorRunner(self.test_dir)
        self.lang_to_template_file = {
            "cpp": "template.cpp",
            "java": "template.java"
        }
        self.lang_to_code_generator = {
            "cpp": CppCodeGenerator,
            "java": JavaCodeGenerator,
        }
    def tearDown(self):
        self.test_data_util.remove_dir()

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
        self.assertEqual(load_intermediate_format(py_test_name), str(response.simple_format))
        self.assertEqual(load_intermediate_types(py_test_name), str(response.types))
        self.assertEqual(load_generated_code(py_test_name, lang),
                         self.get_generator(lang).generate_code(self.get_template(lang), response.original_result))

    def get_template(self, lang: str) -> str:
        file = os.path.join(RESOURCE_DIR, self.lang_to_template_file[lang])
        with open(file, 'r') as f:
            return f.read()

    def get_generator(self, lang: str) -> CodeGenerator:
        return self.lang_to_code_generator[lang]()

if __name__ == "__main__":
    unittest.main()
