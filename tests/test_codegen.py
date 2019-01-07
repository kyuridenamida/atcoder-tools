import sys
import tempfile
import unittest
import os

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.langs import cpp, java
from atcodertools.codegen.template_engine import render
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
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
        self.lang_to_code_generator_func = {
            "cpp": cpp.generate_template_parameters,
            "java": java.generate_template_parameters,
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

    def test_nested_embeddings_on_template(self):
        def _load_text_file(filename):
            with open(os.path.join(RESOURCE_DIR, "test_nested_embeddings_on_template", filename), 'r') as f:
                return f.read()

        def _trim(text):
            return "\n".join([l.rstrip() for l in text.split("\n")])

        template = _load_text_file("template.txt")
        self.assertEqual(_load_text_file("answer_x_0_y_2.txt"),
                         _trim(render(template, x=0, y=2)))
        self.assertEqual(_load_text_file("answer_x_none_y_2.txt"),
                         _trim(render(template, x=None, y=2)))

    def verify(self,
               response: Response,
               py_test_name: str,
               lang: str,
               template_type: str = "old",
               constants: ProblemConstantSet = ProblemConstantSet()):
        self.assertEqual(
            load_intermediate_format(py_test_name),
            str(response.simple_format))
        self.assertEqual(
            load_intermediate_types(py_test_name),
            str(response.types))
        self.assertEqual(load_generated_code(py_test_name, lang),
                         render(
                             self.get_template(lang, template_type),
                             **self.lang_to_code_generator_func[lang](
                                 response.original_result,
                                 constants,
                                 CodeStyleConfig()
                             )
                         ))

    def get_template(self, lang: str, template_type: str) -> str:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang][template_type])
        with open(template_file, 'r') as f:
            return f.read()


if __name__ == "__main__":
    unittest.main()
