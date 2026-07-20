import unittest

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)


class _LegacyConfig:
    pass


class _LengthIndex:

    def get_length(self):
        return "2^N"


class TestLegacyConfigLanguageFallback(unittest.TestCase):

    def test_missing_lang_preserves_existing_expression(self):
        generator = UniversalCodeGenerator.__new__(
            UniversalCodeGenerator
        )

        generator._config = _LegacyConfig()

        generator.info = {
            "insert_space_around_operators": False,
        }

        self.assertEqual(
            generator._get_length(
                _LengthIndex()
            ),
            "2^N",
        )
