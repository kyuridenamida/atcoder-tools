import json
import subprocess
import sys
import unittest

from atcodertools.codegen.tagged_query_python_generator import (
    TaggedQueryPythonGenerator,
)
from atcodertools.fmtprediction.tagged_query import (
    predict_tagged_queries,
)
from tests.test_tagged_query_prediction import (
    make_content,
)


class TestTaggedQueryPythonCodegen(
    unittest.TestCase
):
    def test_generated_reader_executes(
        self,
    ):
        content = make_content()

        prediction = predict_tagged_queries(
            content
        )

        generator = (
            TaggedQueryPythonGenerator(
                prediction.format,
                (
                    "N, Q = map("
                    "int, input().split())"
                ),
            )
        )

        input_part = (
            generator.generate_input_part(
                indent=" " * 4
            )
        )

        program = "\n".join(
            [
                "import json",
                "import sys",
                "def main():",
                input_part,
                (
                    "    remaining = "
                    "sys.stdin.read()"
                ),
                (
                    "    print(json.dumps("
                    "[N, Q, queries, "
                    "remaining]))"
                ),
                "main()",
            ]
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                program,
            ],
            input=(
                content
                .get_samples()[0]
                .get_input()
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        self.assertEqual(
            [
                5,
                4,
                [
                    [1, 10],
                    [2, "hello", 20],
                    [1, 30],
                    [2, "world", 40],
                ],
                "",
            ],
            json.loads(
                completed.stdout
            ),
        )

    def test_generated_reader_rejects_bad_arity(
        self,
    ):
        content = make_content()

        prediction = predict_tagged_queries(
            content
        )

        generator = (
            TaggedQueryPythonGenerator(
                prediction.format,
                (
                    "N, Q = map("
                    "int, input().split())"
                ),
            )
        )

        program = "\n".join(
            [
                "def main():",
                generator.generate_input_part(
                    indent=" " * 4
                ),
                "main()",
            ]
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                program,
            ],
            input=(
                "5 1\n"
                "2 only_one_argument\n"
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertNotEqual(
            0,
            completed.returncode,
        )

        self.assertIn(
            "invalid query arity",
            completed.stderr,
        )


if __name__ == "__main__":
    unittest.main()
