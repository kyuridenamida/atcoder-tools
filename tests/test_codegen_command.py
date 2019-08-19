import io
import os
import unittest

from atcodertools.client.models.contest import Contest
from atcodertools.client.models.problem import Problem
from atcodertools.tools.codegen import main, get_problem_from_url

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_codegen_command/")
TEMPLATE_PATH = os.path.join(RESOURCE_DIR, "template_jinja.cpp")


class TestCodeGenCommand(unittest.TestCase):

    def test_generate_code(self):
        config_path = os.path.join(RESOURCE_DIR, "test_codegen_command.toml")
        answer_file_path = os.path.join(RESOURCE_DIR, "generated_code.cpp")
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

        with open(answer_file_path) as f2:
            self.assertEqual(f1.getvalue(), f2.read())

    def test_url_parser(self):
        problem = Problem(Contest("utpc2014"), "Z", "utpc2014_k")
        urls = [
            "http://utpc2014.contest.atcoder.jp/tasks/utpc2014_k",
            "http://beta.atcoder.jp/contests/utpc2014/tasks/utpc2014_k",
            "http://atcoder.jp/contests/utpc2014/tasks/utpc2014_k",
            "https://utpc2014.contest.atcoder.jp/tasks/utpc2014_k",
            "https://beta.atcoder.jp/contests/utpc2014/tasks/utpc2014_k",
            "https://atcoder.jp/contests/utpc2014/tasks/utpc2014_k",
            "https://atcoder.jp/contests/utpc2014/tasks/utpc2014_k?lang=en",
            "https://atcoder.jp/contests/utpc2014/tasks/utpc2014_k/?lang=en",
        ]

        for url in urls:
            self.assertEqual(
                get_problem_from_url(url).to_dict(), problem.to_dict())


if __name__ == '__main__':
    unittest.main()
