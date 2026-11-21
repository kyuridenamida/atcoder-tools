import os
import unittest
import shutil
import tempfile
from unittest import mock

from atcodertools.tools import compiler

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_tester/"))


class TestTester(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_compiler(self):
        test_dir = os.path.join(self.temp_dir, "test")
        shutil.copytree(os.path.join(
            RESOURCE_DIR, "test_compiler_and_tester"), test_dir)
        os.chdir(test_dir)
        compiler.main(
            '', ["--compile-command", "touch compile-command-success"])
        lst = os.listdir('./')
        self.assertTrue("compile-command-success" in lst)

    @mock.patch("atcodertools.tools.compiler.compile_main_and_judge_programs")
    def test_compile_only_when_diff_detected_option(self, compile_mock):
        os.chdir(os.path.join(RESOURCE_DIR, "test_compiler_and_tester"))
        for value, force_compile in [("false", True), ("true", False)]:
            compiler.main('', ["--compile-only-when-diff-detected", value])
            self.assertEqual(
                force_compile, compile_mock.call_args[1]["force_compile"])


if __name__ == '__main__':
    unittest.main()
