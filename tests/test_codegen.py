import os
import sys
import tempfile
import unittest

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.config.postprocess_config import _run_command
from atcodertools.fileutils.create_contest_file import create_code
from atcodertools.fmtprediction.predict_format import predict_format

from atcodertools.codegen.code_generators import cpp, java
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.tools.templates import get_default_template_path
from atcodertools.tools.tester import run_program
from tests.utils.fmtprediction_test_runner import FormatPredictionTestRunner, Response
from tests.utils.gzip_controller import make_tst_data_controller

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
            "cpp": cpp.main,
            "java": java.main,
        }

    def tearDown(self):
        self.test_data_controller.remove_dir()

    def test_long_case(self):
        response = self.runner.run('rco-contest-2017-qual-B')
        for l in LANGS:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_two_dimensional_case(self):
        response = self.runner.run('abc079-D')
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

    def test_default_code_generators_and_templates(self):
        UNIT_TEST_RESOURCE_DIR = os.path.join(
            RESOURCE_DIR, "test_default_code_generators_and_templates")

        def _load_text_file(filename):
            with open(os.path.join(UNIT_TEST_RESOURCE_DIR, filename), 'r') as f:
                return f.read()

        input_file_path = os.path.join(UNIT_TEST_RESOURCE_DIR, "input.txt")
        expected_output = _load_text_file("output.txt")
        pred_result = predict_format(
            ProblemContent(_load_text_file("format.txt"), [Sample(_load_text_file("input.txt"), None)]))
        code_file = os.path.join(self.temp_dir, "code.cpp")
        exec_file = os.path.join(self.temp_dir, "a.out")
        compile_cmd = "g++ {} -o {} -std=c++14".format(code_file, exec_file)

        # Test compile with default templates

        with open(get_default_template_path("cpp")) as f:
            default_template = f.read()

        self._compile_and_run(
            pred_result.format,
            default_template,
            _load_text_file("cpp/default_generated_code.cpp"),
            input_file_path,
            compile_cmd,
            code_file,
            exec_file,
        )

        # Test compile with custom templates having echo output of input

        exec_result = self._compile_and_run(
            pred_result.format,
            _load_text_file("cpp/template.cpp"),
            _load_text_file("cpp/generated_code.cpp"),
            input_file_path,
            compile_cmd,
            code_file,
            exec_file,
        )
        self.assertEqual(expected_output, exec_result.output)

    def _compile_and_run(self, format, template, expected_generated_code, input_file, compile_cmd, code_file, exec_file):
        args = CodeGenArgs(
            template=template,
            format_=format,
            constants=ProblemConstantSet(123, "yes", "NO"),
            config=CodeStyleConfig()
        )

        code = cpp.main(args)
        self.assertEqual(expected_generated_code, code)
        create_code(code, code_file)
        print(_run_command(compile_cmd, self.temp_dir))  # TODO: stop calling private function
        exec_result = run_program(exec_file, input_file, 2)
        self.assertEqual(exec_result.status.NORMAL, exec_result.status)
        return exec_result

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
        self.assertEqual(
            load_generated_code(py_test_name, lang),
            self.lang_to_code_generator_func[lang](
                CodeGenArgs(
                    self.get_template(lang, template_type),
                    response.original_result.format,
                    constants,
                    CodeStyleConfig())
            ))

    def get_template(self, lang: str, template_type: str) -> str:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang][template_type])
        with open(template_file, 'r') as f:
            return f.read()


if __name__ == "__main__":
    unittest.main()
