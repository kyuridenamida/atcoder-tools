import unittest
import os
import tempfile

from atcodertools.codegen.code_style_config import CodeStyleConfig, INDENT_TYPE_SPACE, CodeStyleConfigInitError, \
    INDENT_TYPE_TAB
from atcodertools.config.config import Config, ConfigType
from atcodertools.tools import get_default_config_path
from atcodertools.common.language import NIM
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from tests.utils.fmtprediction_test_runner import FormatPredictionTestRunner
from tests.utils.gzip_controller import make_tst_data_controller
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_config/")


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_controller = make_tst_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.test_data_controller.create_dir()
        self.runner = FormatPredictionTestRunner(self.test_dir)

    def test_load_code_style_config(self):
        with open(os.path.join(RESOURCE_DIR, "with_indent_width.toml"), 'r') as f:
            config = Config.load(f, {ConfigType.CODESTYLE}).code_style_config

        self.assertEqual(8, config.indent_width)
        self.assertEqual(INDENT_TYPE_SPACE, config.indent_type)

    def test_load_config(self):
        os.chdir(RESOURCE_DIR)

        with open(os.path.join(RESOURCE_DIR, "all_options.toml"), 'r') as f:
            config = Config.load(
                f, {ConfigType.CODESTYLE, ConfigType.POSTPROCESS})

        self.assertEqual(8, config.code_style_config.indent_width)
        self.assertEqual(INDENT_TYPE_TAB, config.code_style_config.indent_type)

        contest_dir = os.path.join(RESOURCE_DIR, "mock_contest")
        problem_dir = os.path.join(contest_dir, "mock_problem")
        self.assertEqual("problem\nmock_problem\n",
                         config.postprocess_config.execute_on_problem_dir(contest_dir))
        self.assertEqual("contest\nmock_file.txt\n",
                         config.postprocess_config.execute_on_contest_dir(problem_dir))
        with open(config.code_style_config.template_file, 'r') as f:
            self.assertEqual("this is custom_template.cpp", f.read())

    def test_load_config_multi_lang(self):
        os.chdir(RESOURCE_DIR)

        with open(os.path.join(RESOURCE_DIR, "cpp_options.toml"), 'r') as f:
            config = Config.load(
                f, {ConfigType.CODESTYLE, ConfigType.POSTPROCESS})

        self.assertEqual(4, config.code_style_config.indent_width)

        with open(os.path.join(RESOURCE_DIR, "nim_options.toml"), 'r') as f:
            config = Config.load(
                f, {ConfigType.CODESTYLE, ConfigType.POSTPROCESS})

        self.assertEqual(2, config.code_style_config.indent_width)

    def test_load_config_fails_due_to_typo(self):
        try:
            with open(os.path.join(RESOURCE_DIR, "typo_in_postprocess.toml"), 'r') as f:
                Config.load(f, {ConfigType.CODESTYLE})
        except TypeError:
            pass

    def test_load_default_config(self):
        with open(get_default_config_path(), 'r') as f:
            Config.load(f, {ConfigType.CODESTYLE})

    def test_init_code_style_config_with_invalid_parameters(self):
        self._expect_error_when_init_config(
            indent_type='SPACE', indent_width=4)
        self._expect_error_when_init_config(
            indent_type='space', indent_width=-1)
        self._expect_error_when_init_config(
            code_generator_file='not existing module')

        code_generator_file = os.path.join(
            RESOURCE_DIR, "broken_custom_code_generator.py")
        self._expect_error_when_init_config(
            code_generator_file=code_generator_file)
        self._expect_error_when_init_config(
            template_file='not existing path'
        )

    def test_custom_codegen_toml(self):
        response = self.runner.run('abc079-D')
        template_file = os.path.join(
            RESOURCE_DIR,
            "test_custom_codegen_toml/template.nim")
        with open(template_file, 'r') as f:
            template = f.read()
        generated_code_file = os.path.join(
            RESOURCE_DIR,
            "test_custom_codegen_toml/generated_code.nim")
        with open(generated_code_file, 'r') as f:
            generated_code = f.read()
        resource_path = os.path.join(
            RESOURCE_DIR, "test_custom_codegen_toml/nim_custom.toml")
        config = CodeStyleConfig(
            lang=NIM.name, code_generator_toml=str(resource_path))

        code = config.code_generator(
            CodeGenArgs(
                template,
                response.original_result.format,
                ProblemConstantSet(),
                config)
        )

        self.assertEqual(generated_code, code)

    def _expect_error_when_init_config(self, **kwargs):
        try:
            CodeStyleConfig(**kwargs)
            self.fail("Must not reach here")
        except CodeStyleConfigInitError:
            pass

    def test_load_config_compiler(self):
        os.chdir(RESOURCE_DIR)

        with open(os.path.join(RESOURCE_DIR, "compiler_options.toml"), 'r') as f:
            config = Config.load(
                f, {ConfigType.CODESTYLE, ConfigType.COMPILER})

        self.assertEqual(
            True, config.compiler_config.compile_only_when_diff_detected)
        self.assertEqual('g++ main.cpp -o main -std=c++17',
                         config.compiler_config.compile_command)


if __name__ == "__main__":
    unittest.main()
