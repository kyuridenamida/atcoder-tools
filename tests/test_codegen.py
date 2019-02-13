import os
import sys
import tempfile
import unittest
from typing import Tuple, List

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.common.language import ALL_LANGUAGES, Language, CPP, JAVA, RUST
from atcodertools.executils.run_command import run_command
from atcodertools.executils.run_program import run_program
from atcodertools.fileutils.create_contest_file import create_code
from atcodertools.fileutils.load_text_file import load_text_file
from atcodertools.fmtprediction.predict_format import predict_format

from atcodertools.codegen.code_generators import cpp, java, rust
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.tools.templates import get_default_template_path
from tests.utils.fmtprediction_test_runner import FormatPredictionTestRunner, Response
from tests.utils.gzip_controller import make_tst_data_controller

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_codegen/")


def load_generated_code(py_test_name, lang):
    with open(os.path.join(RESOURCE_DIR, py_test_name, lang.name, "generated_code.txt"), 'r') as f:
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
            CPP: {
                "old": "template.cpp",
                "jinja": "template_jinja.cpp",
            },
            JAVA: {
                "old": "template.java",
                "jinja": "template_jinja.java",
            },
            RUST: {
                "old": "template.rust",
                "jinja": "template_jinja.rust",
            }
        }
        self.lang_to_code_generator_func = {
            CPP: cpp.main,
            JAVA: java.main,
            RUST: rust.main,
        }
        self.maxDiff = None

    def tearDown(self):
        self.test_data_controller.remove_dir()

    def test_long_case(self):
        response = self.runner.run('rco-contest-2017-qual-B')
        for l in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_two_dimensional_case(self):
        response = self.runner.run('abc079-D')
        for l in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_float_case(self):
        response = self.runner.run('tenka1-2014-qualb-E')
        for l in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, l)

    def test_mod_case(self):
        response = self.runner.run('agc019-E')
        for l in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name,
                        l, "jinja", ProblemConstantSet(mod=998244353))

    def test_yes_no_case(self):
        response = self.runner.run('agc021-C')
        for l in ALL_LANGUAGES:
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
        def _full_path(filename):
            return os.path.join(RESOURCE_DIR, "test_default_code_generators_and_templates", filename)

        input_file = _full_path("input.txt")
        expected_output_file = _full_path("output.txt")
        pred_result = predict_format(
            ProblemContent(
                load_text_file(_full_path("format.txt")),
                [Sample(load_text_file(_full_path("input.txt")), None)]))

        for lang in ALL_LANGUAGES:
            expected_default_generated_code_file = _full_path(
                os.path.join(lang.name, lang.source_code_name("default_generated_code")))

            # Test compile with default templates

            self._compile_and_run(
                lang,
                pred_result.format,
                lang.default_template_path,
                expected_default_generated_code_file,
                input_file
            )

            # Test compile with custom templates having echo output of input

            exec_result = self._compile_and_run(
                lang,
                pred_result.format,
                _full_path(os.path.join(lang.name, lang.source_code_name("template"))),
                _full_path(os.path.join(lang.name, lang.source_code_name("generated_code"))),
                input_file
            )
            self.assertEqual(load_text_file(expected_output_file), exec_result.output)

    def _compile_command(self, lang: Language, code_file: str):
        if lang == CPP:
            return "g++ {} -o a.out -std=c++14".format(code_file)
        elif lang == JAVA:
            return "javac {}".format(code_file)
        elif lang == RUST:
            return "rustc {}".format(code_file)
        else:
            raise NotImplementedError()

    def _exec_file_and_args(self, lang: Language) -> Tuple[str, List[str]]:
        if lang == CPP:
            return "./a.out", []
        elif lang == JAVA:
            return "java", ["Main"]
        elif lang == RUST:
            return "./main", []
        else:
            raise NotImplementedError()

    def _compile_and_run(self, lang, format, template_file, expected_generated_code_file, input_file):
        code_file = os.path.join(self.temp_dir, lang.source_code_name("main"))
        exec_file, exec_args = self._exec_file_and_args(lang)
        compile_cmd = self._compile_command(lang, code_file)

        args = CodeGenArgs(
            template=load_text_file(template_file),
            format_=format,
            constants=ProblemConstantSet(123, "yes", "NO"),
            config=CodeStyleConfig()
        )

        code = lang.default_code_generator(args)
        self.compare_two_source_codes(load_text_file(expected_generated_code_file), code)
        create_code(code, code_file)
        print(run_command(compile_cmd, self.temp_dir))
        exec_result = run_program(exec_file, input_file, 2, exec_args, self.temp_dir)
        self.assertEqual(exec_result.status.NORMAL, exec_result.status)
        return exec_result

    def compare_two_source_codes(self, a: str, b: str):
        a_list = a.split()
        b_list = b.split()
        for x, y in zip(a_list, b_list):
            self.assertEqual(x.rstrip(), y.rstrip())
        self.assertEqual(len(a_list), len(b_list))

    def verify(self,
               response: Response,
               py_test_name: str,
               lang: Language,
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

    def get_template(self, lang: Language, template_type: str) -> str:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang][template_type])
        with open(template_file, 'r') as f:
            return f.read()


if __name__ == "__main__":
    unittest.main()
