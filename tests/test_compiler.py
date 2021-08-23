import os
import unittest
import shutil
import tempfile

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


if __name__ == '__main__':
    unittest.main()
