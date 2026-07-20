from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.format import (
    Format,
)
from atcodertools.fmtprediction.predict_format import (
    _remove_layout_hspace_commands,
    predict_format,
)


FORMAT_WITH_HSPACE = (
    "N M T\n"
    "A_1 B_1\n"
    "A_2 B_2\n"
    "\\hspace{15pt} \\vdots\n"
    "A_M B_M\n"
)

FORMAT_WITHOUT_HSPACE = (
    "N M T\n"
    "A_1 B_1\n"
    "A_2 B_2\n"
    "\\vdots\n"
    "A_M B_M\n"
)

SAMPLES = [
    Sample(
        (
            "10 3 20\n"
            "9 11\n"
            "13 17\n"
            "18 19\n"
        ),
        "",
    ),
    Sample(
        (
            "5 2 7\n"
            "2 4\n"
            "3 6\n"
        ),
        "",
    ),
]


def _content(input_format):
    return ProblemContent(
        input_format_text=input_format,
        input_format_blocks=[
            input_format
        ],
        samples=SAMPLES,
        original_html="",
    )


def test_removes_hspace_and_starred_hspace():
    actual = _remove_layout_hspace_commands(
        (
            "A "
            "\\hspace{15pt}"
            " B "
            "\\hspace*{0.6cm}"
            " C"
        )
    )

    assert actual == "A  B  C"


def test_hspace_layout_predicts_same_format():
    with_hspace = predict_format(
        _content(
            FORMAT_WITH_HSPACE
        )
    )

    without_hspace = predict_format(
        _content(
            FORMAT_WITHOUT_HSPACE
        )
    )

    assert isinstance(
        with_hspace.format,
        Format,
    )

    assert str(
        with_hspace.format
    ) == str(
        without_hspace.format
    )
