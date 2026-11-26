import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.codegen.code_generators import python as python_codegen
from atcodertools.codegen.template_engine import render
from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
)
from atcodertools.fmtprediction.predict_format import predict_format
from atcodertools.fmtprediction.tagged_query import (
    NoTaggedQueryPredictionError,
    predict_tagged_queries,
)
from tests.test_tagged_query_python_codegen_dispatch import (
    TOML_ROOT,
    args_for,
)


def word_tag_content():
    content = ProblemContent(
        input_format_text=(
            "Q\nquery_1\n...\nquery_Q\n"
        ),
        samples=[
            Sample(
                "4\nADD 10 20\nDELETE\nSAVE 7\nLOAD 7\n",
                "",
            ),
            Sample(
                "3\nADD 1 2\nSAVE 3\nLOAD 3\n",
                "",
            ),
        ],
    )
    content.input_format_blocks = [
        "Q\nquery_1\n...\nquery_Q\n",
        "ADD x y\n",
        "DELETE\n",
        "LOAD slot\n",
        "SAVE slot\n",
    ]
    return content


class TestUniversalQueryCodegenAllLanguages(unittest.TestCase):
    def test_word_tags_predict_and_codegen_in_all_languages(self):
        content = word_tag_content()
        raw_prediction = predict_tagged_queries(content)
        self.assertIsInstance(
            raw_prediction.format,
            TaggedQueryFormat,
        )
        self.assertEqual(
            ["ADD", "DELETE", "LOAD", "SAVE"],
            [
                variant.tag
                for variant
                in raw_prediction.format.variants
            ],
        )

        typed_result = predict_format(content)
        self.assertIsInstance(
            typed_result.format,
            TaggedQueryFormat,
        )
        toml_paths = sorted(TOML_ROOT.glob("*.toml"))
        self.assertEqual(10, len(toml_paths))
        for path in toml_paths:
            with self.subTest(language=path.stem):
                parameters = UniversalCodeGenerator(
                    typed_result.format,
                    SimpleNamespace(
                        indent=lambda depth: " " * 4 * depth
                    ),
                    path,
                ).generate_parameters()
                self.assertTrue(
                    parameters["prediction_success"]
                )
                self.assertTrue(
                    parameters["tagged_query"]
                )
                self.assertIn(
                    "queries_tag",
                    parameters["input_part"],
                )
                self.assertIn(
                    "queries_tag",
                    parameters["formal_arguments"],
                )
                self.assertTrue(
                    parameters["query_dispatch_skeleton"]
                )

    def test_default_templates_render_query_skeletons(self):
        typed_result = predict_format(
            word_tag_content()
        )
        self.assertIsInstance(
            typed_result.format,
            TaggedQueryFormat,
        )
        suffixes = {
            "cpp": "cpp",
            "cs": "cs",
            "d": "d",
            "go": "go",
            "java": "java",
            "julia": "jl",
            "nim": "nim",
            "python": "py",
            "rust": "rs",
            "swift": "swift",
        }
        for path in sorted(TOML_ROOT.glob("*.toml")):
            with self.subTest(language=path.stem):
                parameters = UniversalCodeGenerator(
                    typed_result.format,
                    SimpleNamespace(
                        indent=lambda depth: " " * 4 * depth
                    ),
                    path,
                ).generate_parameters()
                template_path = (
                    Path(__file__).parents[1]
                    / "atcodertools"
                    / "tools"
                    / "templates"
                    / "default_template.{}".format(
                        suffixes[path.stem]
                    )
                )
                generated = render(
                    template_path.read_text(),
                    config=SimpleNamespace(
                        indent=lambda depth: " " * 4 * depth
                    ),
                    mod=None,
                    yes_str=None,
                    no_str=None,
                    **parameters
                )
                self.assertIn(
                    "TODO: process this query variant",
                    generated,
                )

    def test_python_default_template_contains_dispatch(self):
        content = word_tag_content()
        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            TaggedQueryFormat,
        )
        template_path = (
            Path(__file__).parents[1]
            / "atcodertools"
            / "tools"
            / "templates"
            / "default_template.py"
        )
        generated = python_codegen.main(
            args_for(
                result.format,
                template_path.read_text(),
            )
        )
        compile(
            generated,
            "<generated-python-query>",
            "exec",
        )
        self.assertIn(
            "for _query in queries:",
            generated,
        )
        self.assertIn(
            "_, x, y = _query",
            generated,
        )
        completed = subprocess.run(
            [sys.executable, "-c", generated],
            input=content.get_samples()[0].get_input(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(
            0,
            completed.returncode,
            completed.stderr + "\n" + generated,
        )

    def test_python_word_tag_entry_executes(self):
        content = word_tag_content()
        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            TaggedQueryFormat,
        )
        template = (
            "#!/usr/bin/env python3\n"
            "from typing import *\n"
            "import json\n"
            "import sys\n"
            "\n"
            "def solve({{ formal_arguments }}):\n"
            "    print(json.dumps(queries))\n"
            "\n"
            "def main():\n"
            "    def iterate_tokens():\n"
            "        for line in sys.stdin:\n"
            "            for word in line.split():\n"
            "                yield word\n"
            "    tokens = iterate_tokens()\n"
            "    {{ input_part }}\n"
            "    solve({{ actual_arguments }})\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )
        generated = python_codegen.main(
            args_for(result.format, template)
        )
        compile(
            generated,
            "<generated-python-word-tag>",
            "exec",
        )
        completed = subprocess.run(
            [sys.executable, "-c", generated],
            input=content.get_samples()[0].get_input(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(
            0,
            completed.returncode,
            completed.stderr + "\n" + generated,
        )
        self.assertIn(
            '["ADD", 10, 20]',
            completed.stdout,
        )
        self.assertIn(
            '["DELETE"]',
            completed.stdout,
        )

    def test_symbol_tags_predict(self):
        content = ProblemContent(
            input_format_text=(
                "Q\nquery_1\n...\nquery_Q\n"
            ),
            samples=[
                Sample(
                    "4\n+ 1 2\n? 3\n- 1\n!\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            "Q\nquery_1\n...\nquery_Q\n",
            "+ x y\n",
            "? x\n",
            "- x\n",
            "!\n",
        ]
        prediction = predict_tagged_queries(
            content
        )
        self.assertEqual(
            ["!", "+", "-", "?"],
            [
                variant.tag
                for variant
                in prediction.format.variants
            ],
        )

    def test_zero_based_eight_variant_numeric_tags_predict(self):
        content = ProblemContent(
            input_format_text=(
                "Q\nquery_1\n...\nquery_Q\n"
            ),
            samples=[
                Sample(
                    (
                        "8\n"
                        "0\n"
                        "1 10\n"
                        "2\n"
                        "3 30\n"
                        "4\n"
                        "5 50\n"
                        "6\n"
                        "7 70\n"
                    ),
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            "Q\nquery_1\n...\nquery_Q\n",
            "0\n",
            "1 x\n",
            "2\n",
            "3 x\n",
            "4\n",
            "5 x\n",
            "6\n",
            "7 x\n",
        ]
        prediction = predict_tagged_queries(content)
        self.assertEqual(
            list(range(8)),
            [
                variant.tag
                for variant
                in prediction.format.variants
            ],
        )

    def test_symbol_and_word_storage_names_do_not_collide(self):
        content = ProblemContent(
            input_format_text=(
                "Q\nquery_1\n...\nquery_Q\n"
            ),
            samples=[
                Sample(
                    "3\n+ 1\nPLUS 2 3\n?\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            "Q\nquery_1\n...\nquery_Q\n",
            "+ x\n",
            "PLUS x y\n",
            "?\n",
        ]
        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            TaggedQueryFormat,
        )
        parameters = UniversalCodeGenerator(
            result.format,
            SimpleNamespace(
                indent=lambda depth: " " * 4 * depth
            ),
            TOML_ROOT / "nim.toml",
        ).generate_parameters()
        storage_names = parameters[
            "query_storage_names"
        ]
        self.assertEqual(
            len(storage_names),
            len(set(storage_names)),
        )
        self.assertIn(
            "queries_symbol_plus_x",
            storage_names,
        )
        self.assertIn(
            "queries_word_plus_x",
            storage_names,
        )

    def test_legacy_numeric_variants_ignore_extended_noise(self):
        content = ProblemContent(
            input_format_text=(
                "Q\nquery_1\n...\nquery_Q\n"
            ),
            samples=[
                Sample(
                    "3\n1 10 20\n2 30\n1 40 50\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            "Q\nquery_1\n...\nquery_Q\n",
            "1 x y\n",
            "2 x\n",
            "4 unrelated a b c d\n",
        ]
        prediction = predict_tagged_queries(content)
        self.assertEqual(
            [1, 2],
            [
                variant.tag
                for variant in prediction.format.variants
            ],
        )

    def test_same_schema_tags_are_not_tagged_queries(self):
        content = ProblemContent(
            input_format_text="Q\nquery_1\n...\nquery_Q\n",
            samples=[
                Sample(
                    "4\n1 10 20\n2 30 40\n1 50 60\n2 70 80\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            "Q\nquery_1\n...\nquery_Q\n",
            "1 x y\n",
            "2 a b\n",
        ]
        with self.assertRaises(NoTaggedQueryPredictionError):
            predict_tagged_queries(content)

        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            HomogeneousQueryFormat,
        )
        self.assertEqual(
            ["query_type", "query_arg_1", "query_arg_2"],
            [
                argument.name
                for argument in result.format.arguments
            ],
        )

    def test_event_window_uses_q_for_homogeneous_queries(self):
        content = ProblemContent(
            input_format_text=(
                "N Q\n"
                "event_1\n"
                "event_2\n"
                "\\vdots\n"
                "event_Q\n"
            ),
            samples=[
                Sample(
                    "3 3\n1 10\n2 20\n3 30\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            (
                "N Q\n"
                "event_1\n"
                "event_2\n"
                "\\vdots\n"
                "event_Q\n"
            ),
            "1 x\n",
            "2 x\n",
            "3 x\n",
        ]
        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            HomogeneousQueryFormat,
        )
        self.assertEqual(
            "Q",
            result.format.query_count_var,
        )

    def test_textrm_query_window_uses_q_for_homogeneous_queries(self):
        content = ProblemContent(
            input_format_text=(
                "N\n"
                "Q\n"
                "\\textrm{query}_1\n"
                "\\textrm{query}_2\n"
                "\\vdots\n"
                "\\textrm{query}_Q\n"
            ),
            samples=[
                Sample(
                    "4\n3\n1 10\n2 20\n3 30\n",
                    "",
                )
            ],
        )
        content.input_format_blocks = [
            (
                "N\n"
                "Q\n"
                "\\textrm{query}_1\n"
                "\\textrm{query}_2\n"
                "\\vdots\n"
                "\\textrm{query}_Q\n"
            ),
            "1 x\n",
            "2 x\n",
            "3 x\n",
        ]
        result = predict_format(content)
        self.assertIsInstance(
            result.format,
            HomogeneousQueryFormat,
        )
        self.assertEqual(
            "Q",
            result.format.query_count_var,
        )


if __name__ == "__main__":
    unittest.main()
