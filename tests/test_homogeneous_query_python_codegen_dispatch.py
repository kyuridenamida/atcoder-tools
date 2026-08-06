import json
import subprocess
import sys
import unittest

from atcodertools.codegen.code_generators import (
    python as python_codegen,
)
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)
from tests.test_homogeneous_query_prediction import (
    make_content,
)
from tests.test_tagged_query_python_codegen_dispatch import (
    TOML_ROOT,
    args_for,
)


class TestHomogeneousQueryPythonCodegenDispatch(
    unittest.TestCase
):
    def test_universal_generator_supports_all_languages(
        self,
    ):
        result = predict_format(
            make_content()
        )
        self.assertIsInstance(
            result.format,
            HomogeneousQueryFormat,
        )
        args = args_for(
            result.format,
            "{{ input_part }}",
        )
        toml_paths = sorted(
            TOML_ROOT.glob("*.toml")
        )
        self.assertEqual(10, len(toml_paths))
        for path in toml_paths:
            with self.subTest(language=path.stem):
                parameters = UniversalCodeGenerator(
                    result.format,
                    args.config,
                    path,
                ).generate_parameters()
                self.assertTrue(
                    parameters["prediction_success"]
                )
                self.assertFalse(
                    parameters["tagged_query"]
                )
                self.assertTrue(
                    parameters["homogeneous_query"]
                )
                self.assertTrue(
                    parameters["query_dispatch_skeleton"]
                )

    def test_python_codegen_entry_executes(
        self,
    ):
        content = make_content()

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
                    [1, 3],
                    [2, 5],
                ],
                "",
            ],
            json.loads(
                completed.stdout
            ),
        )


if __name__ == "__main__":
    unittest.main()
