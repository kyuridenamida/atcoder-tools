import unittest

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
    get_builtin_code_generator_info_toml_path,
)
from atcodertools.codegen.code_style_config import (
    CodeStyleConfig,
)
from atcodertools.common.language import (
    ALL_LANGUAGES,
)
from atcodertools.fmtprediction.predict_format import (
    _fixed_index_alias,
    _normalize_indexed_identifier_aliases,
    predict_format,
)


FORMAT_TEXT = r"""N_1
u_{1,1} v_{1,1}
\vdots
u_{1,N_1-1} v_{1,N_1-1}
N_2
u_{2,1} v_{2,1}
\vdots
u_{2,N_2-1} v_{2,N_2-1}
"""

NORMALIZED_FORMAT_TEXT = r"""Nfixedone
ufixedone_{1} vfixedone_{1}
\vdots
ufixedone_{Nfixedone-1} vfixedone_{Nfixedone-1}
Nfixedtwo
ufixedtwo_{1} vfixedtwo_{1}
\vdots
ufixedtwo_{Nfixedtwo-1} vfixedtwo_{Nfixedtwo-1}
"""

SAMPLE_TEXT = """3
1 2
2 3
4
1 2
2 3
3 4
"""


class _Sample:
    def __init__(self, input_text):
        self._input_text = input_text

    def get_input(self):
        return self._input_text


class _Content:
    original_html = None

    def __init__(
        self,
        input_format,
        sample_text,
    ):
        self._input_format = input_format
        self._samples = [
            _Sample(sample_text)
        ]

    def get_input_format(self):
        return self._input_format

    def get_input_format_blocks(self):
        return [self._input_format]

    def get_input_format_context(self):
        return self._input_format

    def get_samples(self):
        return list(self._samples)


class TestIndexedIdentifierNormalization(
    unittest.TestCase,
):
    def test_normalizes_independent_fixed_segments(
        self,
    ):
        self.assertEqual(
            _normalize_indexed_identifier_aliases(
                FORMAT_TEXT
            ),
            NORMALIZED_FORMAT_TEXT,
        )

    def test_preserves_ordinary_one_dimensional_array(
        self,
    ):
        source = (
            "N\n"
            "A_1 A_2 \\ldots A_N\n"
        )

        self.assertEqual(
            _normalize_indexed_identifier_aliases(
                source
            ),
            source,
        )

    def test_preserves_dense_two_dimensional_array(
        self,
    ):
        source = (
            "H W\n"
            "A_{1,1} A_{1,2} \\ldots A_{1,W}\n"
            "\\vdots\n"
            "A_{H,1} A_{H,2} \\ldots A_{H,W}\n"
        )

        self.assertEqual(
            _normalize_indexed_identifier_aliases(
                source
            ),
            source,
        )

    def test_preserves_standalone_indexed_scalar_without_segments(
        self,
    ):
        source = (
            "N_1\n"
            "A_1 A_2 \\ldots A_{N_1}\n"
        )

        self.assertEqual(
            _normalize_indexed_identifier_aliases(
                source
            ),
            source,
        )

    def test_predicts_abc401f_shape(
        self,
    ):
        result = predict_format(
            _Content(
                FORMAT_TEXT,
                SAMPLE_TEXT,
            )
        )

        rendered = str(result.format)

        self.assertEqual(
            rendered,
            (
                "[(Singular: Nfixedone),"
                "(Parallel: ufixedone,"
                "vfixedone | 1 to "
                "Nfixedone-1),"
                "(Singular: Nfixedtwo),"
                "(Parallel: ufixedtwo,"
                "vfixedtwo | 1 to "
                "Nfixedtwo-1)]"
            ),
        )

    def test_aliases_are_portable_identifiers(
        self,
    ):
        normalized = (
            _normalize_indexed_identifier_aliases(
                FORMAT_TEXT
            )
        )

        generated = [
            _fixed_index_alias(
                base,
                literal,
            )
            for base, literal in (
                ("N", "1"),
                ("N", "2"),
                ("u", "1"),
                ("u", "2"),
                ("v", "1"),
                ("v", "2"),
            )
        ]

        for identifier in generated:
            self.assertIn(
                identifier,
                normalized,
            )
            self.assertRegex(
                identifier,
                r"^[A-Za-z]+$",
            )
            self.assertNotIn(
                "_",
                identifier,
            )

    def test_all_languages_generate_parameters(
        self,
    ):
        result = predict_format(
            _Content(
                FORMAT_TEXT,
                SAMPLE_TEXT,
            )
        )

        success_count = 0

        for language in ALL_LANGUAGES:
            generator = UniversalCodeGenerator(
                result.format,
                CodeStyleConfig(
                    lang=language.name
                ),
                get_builtin_code_generator_info_toml_path(
                    language.name
                ),
            )

            parameters = (
                generator.generate_parameters()
            )

            self.assertTrue(
                parameters.get(
                    "prediction_success"
                )
            )

            success_count += 1

        self.assertEqual(
            success_count,
            len(ALL_LANGUAGES),
        )


if __name__ == "__main__":
    unittest.main()
