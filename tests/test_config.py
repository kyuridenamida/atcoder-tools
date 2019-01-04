import unittest
import os

from atcodertools.codegen.code_style_config import CodeStyleConfig, INDENT_TYPE_SPACE, CodeStyleConfigInitError, \
    INDENT_TYPE_TAB
from atcodertools.config.config import Config

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
        with open(os.path.join(RESOURCE_DIR, "all_options.toml"), 'r') as f:
            config = Config.load(f)

        self.assertEqual(8, config.code_style_config.indent_width)
        self.assertEqual(INDENT_TYPE_TAB, config.code_style_config.indent_type)

        contest_dir = os.path.join(RESOURCE_DIR, "mock_contest")
        problem_dir = os.path.join(contest_dir, "mock_problem")
        self.assertEqual("problem\nmock_problem\n",
                         config.postprocess_config.execute_for_problem(contest_dir))
        self.assertEqual("contest\nmock_file.txt\n",
                         config.postprocess_config.execute_for_contest(problem_dir))

    def test_init_code_style_config_with_invalid_parameters(self):
        self._expect_error_when_init_config(
            indent_type='SPACE', indent_width=4)
        self._expect_error_when_init_config(
            indent_type='space', indent_width=-1)

    def _expect_error_when_init_config(self, **kwargs):
        try:
            CodeStyleConfig(**kwargs)
            self.fail("Must not reach here")
        except CodeStyleConfigInitError:
            pass


if __name__ == "__main__":
    unittest.main()
