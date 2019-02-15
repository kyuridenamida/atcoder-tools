import io
import os
import unittest

from atcodertools.tools.codegen import main

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_codegen_command/")
TEMPLATE_PATH = os.path.join(RESOURCE_DIR, "template_jinja.cpp")


class TestCodeGenCOmmand(unittest.TestCase):

    def test_generate_code(self):
        answer_data_dir_path = os.path.join(
            RESOURCE_DIR,
            "test_prepare_workspace")

        config_path = os.path.join(RESOURCE_DIR, "test_codegen_command.toml")
        correct_file_path = os.path.join(RESOURCE_DIR, "generated_code.cpp")
        f1 = io.StringIO()

        main(
            "",
            ["https://atcoder.jp/contests/abc012/tasks/abc012_4",
             "--template", TEMPLATE_PATH,
             "--lang", "cpp",
             "--without-login",
             '--config', config_path
             ],
            output_file=f1
        )

        with open(correct_file_path) as f2:
            self.assertEqual(f1.getvalue(), f2.read())


if __name__ == '__main__':
    unittest.main()
