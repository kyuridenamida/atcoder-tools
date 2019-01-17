import unittest
import os

from atcodertools.codegen.code_style_config import CodeStyleConfig, INDENT_TYPE_SPACE, CodeStyleConfigInitError, \
    INDENT_TYPE_TAB
from atcodertools.config.config import Config
from atcodertools.tools import get_default_config_path

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_config/")


class TestConfig(unittest.TestCase):

    def test_load_code_style_config(self):
        with open(os.path.join(RESOURCE_DIR, "with_indent_width.toml"), 'r') as f:
            config = Config.load(f).code_style_config

        self.assertEqual(8, config.indent_width)
        self.assertEqual(INDENT_TYPE_SPACE, config.indent_type)

    def test_load_config(self):
        os.chdir(RESOURCE_DIR)

        with open(os.path.join(RESOURCE_DIR, "all_options.toml"), 'r') as f:
            config = Config.load(f)

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

    def test_load_config_fails_due_to_typo(self):
        try:
            with open(os.path.join(RESOURCE_DIR, "typo_in_postprocess.toml"), 'r') as f:
                Config.load(f)
        except TypeError:
            pass

    def test_load_default_config(self):
        with open(get_default_config_path(), 'r') as f:
            Config.load(f)

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

    def _expect_error_when_init_config(self, **kwargs):
        try:
            CodeStyleConfig(**kwargs)
            self.fail("Must not reach here")
        except CodeStyleConfigInitError:
            pass


if __name__ == "__main__":
    unittest.main()
