import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from atcodertools.codegen.code_generators import (
    python as python_codegen,
)
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)
from tests.test_tagged_query_predict_format_bridge import (
    tagged_query_content,
)


ROOT = Path(__file__).resolve().parents[1]

TOML_ROOT = (
    ROOT
    / "atcodertools"
    / "codegen"
    / "code_generators"
    / "universal_generator"
)


class Config:
    def indent(
        self,
        depth,
    ):
        return " " * 4 * depth


def args_for(
    format_,
    template,
):
    return SimpleNamespace(
        format=format_,
        config=Config(),
        template=template,
        constants=SimpleNamespace(
            mod=1000000007,
            yes_str="Yes",
            no_str="No",
        ),
    )


class TestTaggedQueryPythonCodegenDispatch(
    unittest.TestCase
):
    def test_universal_generator_supports_all_languages(
        self,
    ):
        result = predict_format(
            tagged_query_content()
        )
        toml_paths = sorted(
            TOML_ROOT.glob("*.toml")
        )
        self.assertEqual(10, len(toml_paths))
        for path in toml_paths:
            with self.subTest(language=path.stem):
                parameters = UniversalCodeGenerator(
                    result.format,
                    Config(),
                    path,
                ).generate_parameters()
                self.assertTrue(
                    parameters["prediction_success"]
                )
                self.assertTrue(
                    parameters["tagged_query"]
                )
                self.assertFalse(
                    parameters["homogeneous_query"]
                )
                self.assertTrue(
                    parameters["query_dispatch_skeleton"]
                )

    def test_python_codegen_entry_executes(
        self,
    ):
        content = tagged_query_content()

        result = predict_format(
            content
        )

        template = """#!/usr/bin/env python3
from typing import *
import json
import sys

# FORMAL={{ formal_arguments }}
# ACTUAL={{ actual_arguments }}

def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word

    tokens = iterate_tokens()
    {% if prediction_success %}
    {{ input_part }}
    print(json.dumps([
        queries,
        sys.stdin.read(),
    ]))
    {% else %}
    raise RuntimeError("prediction failed")
    {% endif %}

if __name__ == "__main__":
    main()
"""

        generated = python_codegen.main(
            args_for(
                result.format,
                template,
            )
        )

        self.assertIn(
            "queries: List[Tuple]",
            generated,
        )

        self.assertIn(
            "ACTUAL=N, Q, queries",
            generated,
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                generated,
            ],
            input=(
                content
                .get_samples()[0]
                .get_input()
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertEqual(
            0,
            completed.returncode,
            completed.stderr
            + "\n"
            + generated,
        )

        self.assertEqual(
            [
                [
                    [1, 10, 20],
                    [2],
                    [1, 30, 40],
                    [2],
                ],
                "",
            ],
            json.loads(
                completed.stdout
            ),
        )


if __name__ == "__main__":
    unittest.main()
