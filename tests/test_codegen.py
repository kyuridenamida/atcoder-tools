import os
import re
import sys
import tempfile
import unittest
from typing import Tuple, List

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.common.language import ALL_LANGUAGES, Language, CPP, JAVA, RUST, PYTHON, NIM, DLANG, CSHARP, SWIFT, GO, JULIA
from atcodertools.executils.run_command import run_command
from atcodertools.executils.run_program import run_program
from atcodertools.fileutils.create_contest_file import create_code
from atcodertools.fileutils.load_text_file import load_text_file
from atcodertools.fmtprediction.predict_format import predict_format

from atcodertools.codegen.code_generators import cpp, java, rust, python, nim, d, cs, swift, go, julia
from atcodertools.codegen.code_style_config import CodeStyleConfig, INDENT_TYPE_SPACE, INDENT_TYPE_TAB
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
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
            },
            PYTHON: {
                "old": "template.py",
                "jinja": "template_jinja.py",
            },
            NIM: {
                "old": "template.nim",
                "jinja": "template_jinja.nim",
            },
            DLANG: {
                "old": "template.d",
                "jinja": "template_jinja.d",
            },
            CSHARP: {
                "old": "template.cs",
                "jinja": "template_jinja.cs",
            },
            SWIFT: {
                "old": "template.swift",
                "jinja": "template_jinja.swift",
            },
            GO: {
                "old": "template.go",
                "jinja": "template_jinja.go",
            },
            JULIA: {
                "old": "template.jl",
                "jinja": "template_jinja.jl",
            },
        }
        self.lang_to_code_generator_func = {
            CPP: cpp.main,
            JAVA: java.main,
            RUST: rust.main,
            PYTHON: python.main,
            NIM: nim.main,
            DLANG: d.main,
            CSHARP: cs.main,
            SWIFT: swift.main,
            GO: go.main,
            JULIA: julia.main,
        }
        self.maxDiff = None

    def tearDown(self):
        self.test_data_controller.remove_dir()

    def test_long_case(self):
        response = self.runner.run('rco-contest-2017-qual-B')
        for lang in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, lang)

    def test_two_dimensional_case(self):
        response = self.runner.run('abc079-D')
        for lang in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, lang)

    def test_float_case(self):
        response = self.runner.run('tenka1-2014-qualb-E')
        for lang in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, lang)

    def test_mod_case(self):
        response = self.runner.run('agc019-E')
        for lang in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name,
                        lang, "jinja", ProblemConstantSet(mod=998244353))

    def test_yes_no_case(self):
        response = self.runner.run('agc021-C')
        for lang in ALL_LANGUAGES:
            self.verify(response, sys._getframe().f_code.co_name, lang, "jinja",
                        ProblemConstantSet(yes_str="YES", no_str="NO"))

    def test_nested_embeddings_on_template(self):
        def _load_text_file(filename):
            with open(os.path.join(RESOURCE_DIR, "test_nested_embeddings_on_template", filename), 'r') as f:
                return f.read()

        def _trim(text):
            return "\n".join([lang.rstrip() for lang in text.split("\n")])

        template = _load_text_file("template.txt")
        self.assertEqual(_load_text_file("answer_x_0_y_2.txt"),
                         _trim(render(template, x=0, y=2)))
        self.assertEqual(_load_text_file("answer_x_none_y_2.txt"),
                         _trim(render(template, x=None, y=2)))

    def test_indent_estimation(self):
        def _load_text_file(filename):
            with open(os.path.join(RESOURCE_DIR, "test_indent_estimation", filename), 'r') as f:
                return f.read()

        def _trim(text):
            return "\n".join([lang.rstrip() for lang in text.split("\n")])

        template = _load_text_file("template.txt")
        self.assertEqual(_load_text_file("answer_space_2.txt"),
                         _trim(render(template, config=CodeStyleConfig(indent_type=INDENT_TYPE_SPACE, indent_width=2), input_part=_load_text_file("indent_space_2.txt"))))
        self.assertEqual(_load_text_file("answer_space_4.txt"),
                         _trim(render(template, config=CodeStyleConfig(indent_type=INDENT_TYPE_SPACE, indent_width=4), input_part=_load_text_file("indent_space_4.txt"))))
        self.assertEqual(_load_text_file("answer_tab.txt"),
                         _trim(render(template, config=CodeStyleConfig(indent_type=INDENT_TYPE_TAB), input_part=_load_text_file("indent_tab.txt"))))

    def test_default_code_generators_and_templates(self):
        def _full_path(filename):
            return os.path.join(RESOURCE_DIR, "test_default_code_generators_and_templates", filename)

        input_file = _full_path("echo_test_input.txt")
        expected_output_file = _full_path("echo_test_output.txt")
        pred_result = predict_format(
            ProblemContent(
                load_text_file(_full_path("echo_test_format.txt")),
                [Sample(load_text_file(_full_path("echo_test_input.txt")), None)]), True)

        for lang in ALL_LANGUAGES:
            expected_default_generated_code_file = _full_path(
                os.path.join(lang.name, lang.source_code_name("expected_default_generated_code")))

            # 1. Compile test with default templates

            self._compile_and_run(
                lang,
                pred_result.format,
                lang.default_template_path,
                expected_default_generated_code_file,
                input_file
            )

            # 2. Echo test, which tests custom templates having echo output of input

            exec_result = self._compile_and_run(
                lang,
                pred_result.format,
                _full_path(os.path.join(
                    lang.name, lang.source_code_name("echo_template"))),
                _full_path(os.path.join(lang.name, lang.source_code_name(
                    "expected_echo_generated_code"))),
                input_file
            )
            self.assertEqual(load_text_file(
                expected_output_file), exec_result.output)

    def _compile_command(self, lang: Language, code_file: str):
        if lang == CPP:
            return "g++ {} -o a.out -std=c++20".format(code_file)
        elif lang == JAVA:
            return "javac {}".format(code_file)
        elif lang == RUST:
            return "rustc {}".format(code_file)
        elif lang == PYTHON:
            return "python3 -mpy_compile {}".format(code_file)
        elif lang == NIM:
            return "nim c {}".format(code_file)
        elif lang == DLANG:
            return "dmd {} -of=main".format(code_file)
        elif lang == CSHARP:
            return "mcs {}".format(code_file)
        elif lang == SWIFT:
            return "swiftc {} -o main".format(code_file)
        elif lang == GO:
            return "go build -o main {}".format(code_file)
        elif lang == JULIA:
            return ""
        else:
            raise NotImplementedError()

    def _exec_file_and_args(self, lang: Language) -> Tuple[str, List[str]]:
        if lang == CPP:
            return "./a.out", []
        elif lang == JAVA:
            return "java", ["Main"]
        elif lang == RUST:
            return "./main", []
        elif lang == PYTHON:
            return "python3", ["main.py"]
        elif lang == NIM:
            return "./main", []
        elif lang == DLANG:
            return "./main", []
        elif lang == CSHARP:
            return "mono", ["main.exe"]
        elif lang == SWIFT:
            return "./main", []
        elif lang == GO:
            return "./main", []
        elif lang == JULIA:
            return "julia", ["main.jl"]
        else:
            raise NotImplementedError()

    def _clean_up(self, lang: Language):
        if lang == CPP:
            os.remove(os.path.join(self.temp_dir, "a.out"))
        elif lang == JAVA:
            return
        elif lang == RUST:
            os.remove(os.path.join(self.temp_dir, "main"))
        elif lang == PYTHON:
            return
        elif lang == NIM:
            os.remove(os.path.join(self.temp_dir, "main"))
        elif lang == DLANG:
            os.remove(os.path.join(self.temp_dir, "main"))
        elif lang == CSHARP:
            os.remove(os.path.join(self.temp_dir, "main.exe"))
        elif lang == SWIFT:
            os.remove(os.path.join(self.temp_dir, "main"))
        elif lang == GO:
            os.remove(os.path.join(self.temp_dir, "main"))
        elif lang == JULIA:
            return
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
            config=CodeStyleConfig(lang=lang.name)
        )
        code = lang.default_code_generator(args)
        # to remove version strings from test resources
        code = re.sub(r'Generated by \d+(\.\d+)+', 'Generated by x.y.z', code)
        self.compare_two_texts_ignoring_trailing_spaces(
            load_text_file(expected_generated_code_file), code)
        create_code(code, code_file)
        try:
            print("Executing:", compile_cmd)
            print(run_command(compile_cmd, self.temp_dir))

            print("Run program:", [exec_file] + exec_args)
            exec_result = run_program(
                exec_file, input_file, 2, exec_args, self.temp_dir)
        finally:
            self._clean_up(lang)

        print("== stdout ==")
        print(exec_result.output)
        print("== stderr ==")
        print(exec_result.stderr)

        self.assertEqual(exec_result.status.NORMAL, exec_result.status)
        return exec_result

    def compare_two_texts_ignoring_trailing_spaces(self, expected: str, output: str):
        a_list = expected.split()
        b_list = output.split()
        has_diff = False
        for x, y in zip(a_list, b_list):
            has_diff = has_diff or x.rstrip() != y.rstrip()
        has_diff = has_diff or len(a_list) != len(b_list)
        if has_diff:
            self.assertEqual(expected, output)

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
                    CodeStyleConfig(lang=lang.name))
            ))

    def get_template(self, lang: Language, template_type: str) -> str:
        template_file = os.path.join(
            RESOURCE_DIR,
            self.lang_to_template_file[lang][template_type])
        with open(template_file, 'r') as f:
            return f.read()


if __name__ == "__main__":
    unittest.main()
