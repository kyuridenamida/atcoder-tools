from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
    _normalize_layout_tex_commands,
    predict_format,
)


def _content(input_format):
    return ProblemContent(
        input_format_text=input_format,
        input_format_blocks=[
            input_format
        ],
        samples=[
            Sample(
                "3\n10 20 30\n",
                "",
            ),
        ],
        original_html="",
    )


def test_normalizes_tex_styles_and_spaced_indices():
    actual = _normalize_layout_tex_commands(
        (
            r"\mathrm { A } _ { i , j } "
            r"\text{B} _ 2"
        )
    )

    assert actual == "A_{i,j} B_2"


def test_preserves_query_and_operation_placeholders():
    source = (
        r"\text{query}_1 "
        r"\mathrm{Query}_Q "
        r"\mathrm{op}_M "
        r"\text{operation}_K "
        r"\text{case}_T "
        r"\mathrm{testcase}_T"
    )

    assert (
        _normalize_layout_tex_commands(source)
        == source
    )


def test_preserves_plain_command_like_identifiers():
    source = (
        "text mathrm hspace rm it "
        "item iteration"
    )

    assert (
        _normalize_layout_tex_commands(source)
        == source
    )


def test_end_to_end_prediction_uses_normalized_view():
    decorated = (
        "N\n"
        r"\mathrm { A } _ { 1 } "
        r"\hspace{5pt} \ldots "
        r"\mathrm { A } _ { N }"
        "\n"
    )

    canonical = (
        "N\n"
        "A_1 \\ldots A_N\n"
    )

    decorated_content = _content(
        decorated
    )
    raw_blocks = (
        decorated_content.get_input_format_blocks()
    )

    decorated_result = predict_format(
        decorated_content
    )
    canonical_result = predict_format(
        _content(canonical)
    )

    assert (
        str(decorated_result.format)
        == str(canonical_result.format)
    )

    assert (
        decorated_content.get_input_format_blocks()
        == raw_blocks
    )
