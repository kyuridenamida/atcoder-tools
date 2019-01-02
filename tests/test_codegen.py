import sys
import tempfile
import unittest
import os

from atcodertools.codegen.code_gen_config import CodeGenConfig, INDENT_TYPE_SPACE, ConfigInitError
from atcodertools.codegen.code_generator import CodeGenerator
from atcodertools.codegen.java_code_generator import JavaCodeGenerator
from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from tests.utils.gzip_controller import make_tst_data_controller
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
        self.test_data_controller = make_tst_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.test_data_controller.create_dir()
        self.runner = FormatPredictionTestRunner(self.test_dir)
        self.lang_to_template_file = {
            "cpp": {
                "old": "template.cpp",
                "jinja": "template_jinja.cpp",
            },
            "java": {
                "old": "template.java",
                "jinja": "template_jinja.java",
            }
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

    def test_mod_case(self):
        response = self.runner.run('agc019-E')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name,
                        l, "jinja", ProblemConstantSet(mod=998244353))

    def test_yes_no_case(self):
        response = self.runner.run('agc021-C')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name, l, "jinja",
                        ProblemConstantSet(yes_str="YES", no_str="NO"))

    def verify(self, response: Response, py_test_name: str, lang: str, template_type: str = "old",
               constants: ProblemConstantSet = ProblemConstantSet()):
        self.assertEqual(
            load_intermediate_format(py_test_name),
            str(response.simple_format))
        self.assertEqual(
            load_intermediate_types(py_test_name),
            str(response.types))
        self.assertEqual(load_generated_code(py_test_name, lang),
                         self.get_generator(lang, template_type).generate_code(response.original_result, constants))

    def get_generator(self, lang: str, template_type: str) -> CodeGenerator:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang][template_type])
        with open(template_file, 'r') as f:
            return self.lang_to_code_generator[lang](f.read())

    def test_load_code_gen_config(self):
        with open(os.path.join(RESOURCE_DIR, "atcodertools-test.toml"), 'r') as f:
            config = CodeGenConfig.load(f)

        self.assertEqual(8, config.indent_width)
        self.assertEqual(INDENT_TYPE_SPACE, config.indent_type)

    def test_init_code_gen_config_with_invalid_parameters(self):
        self._expect_error_when_init_config(
            indent_type='SPACE', indent_width=4)
        self._expect_error_when_init_config(
            indent_type='space', indent_width=-1)

    def _expect_error_when_init_config(self, **kwargs):
        try:
            CodeGenConfig(**kwargs)
            self.fail("Must not reach here")
        except ConfigInitError:
            pass


if __name__ == "__main__":
    unittest.main()
