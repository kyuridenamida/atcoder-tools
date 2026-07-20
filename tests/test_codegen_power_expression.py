from atcodertools.codegen.code_generators.universal_code_generator import (
    _render_power_of_two_length,
)


def test_power_of_two_length_is_rendered_for_all_builtin_languages():
    expected = {
        "cpp": "(1LL << (N))",
        "cs": "(1 << (int)(N))",
        "d": "(1L << (N))",
        "go": "(1 << (N))",
        "java": "(1 << (int)(N))",
        "julia": "(1 << (N))",
        "nim": "(1 shl (N))",
        "python": "(1 << (N))",
        "rust": "(1usize << ((N) as usize))",
        "swift": "(1 << (N))",
    }

    for language, rendered in expected.items():
        assert (
            _render_power_of_two_length(
                "2^N",
                language,
            )
            == rendered
        )


def test_power_renderer_preserves_non_power_expressions():
    assert (
        _render_power_of_two_length(
            "N-1",
            "python",
        )
        == "N-1"
    )


def test_unknown_language_keeps_existing_contract():
    assert (
        _render_power_of_two_length(
            "2^N",
            "custom",
        )
        == "2^N"
    )


def test_power_renderer_accepts_code_style_language_object():
    from atcodertools.codegen.code_style_config import (
        CodeStyleConfig,
    )
    from atcodertools.common.language import PYTHON

    config = CodeStyleConfig(
        lang=PYTHON.name,
    )

    assert (
        type(config.lang).__name__
        == "Language"
    )

    assert (
        _render_power_of_two_length(
            "2^N",
            config.lang,
        )
        == "(1 << (N))"
    )
