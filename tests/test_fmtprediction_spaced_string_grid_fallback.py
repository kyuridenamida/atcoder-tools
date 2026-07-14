from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
    _collapse_spaced_grid_rows,
    predict_format,
)


def _predict(
    input_format,
    sample_inputs,
):
    content = ProblemContent(
        input_format_text=input_format,
        samples=[
            Sample(
                sample_input,
                "",
            )
            for sample_input
            in sample_inputs
        ],
        original_html="",
    )

    return str(
        predict_format(content).format
    )


def test_spaced_grid_rows_collapse_outer_index():
    actual = _collapse_spaced_grid_rows(
        (
            "H W\n"
            "c_{0,0} c_{0,1} c_{0,W-1}\n"
            "c_{1,0} c_{1,1} c_{1,W-1}\n"
            ":\n"
            "c_{H-1,0} c_{H-1,1} c_{H-1,W-1}\n"
        )
    )

    assert actual == (
        "H W\n"
        "c_{0}\n"
        "c_{1}\n"
        ":\n"
        "c_{H-1}\n"
    )


def test_atc001_a_is_recovered():
    actual = _predict(
        (
            "H W\n"
            "c_{0,0} c_{0,1} c_{0,W-1}\n"
            "c_{1,0} c_{1,1} c_{1,W-1}\n"
            ":\n"
            "c_{H-1,0} c_{H-1,1} c_{H-1,W-1}\n"
        ),
        [
            (
                "4 5\n"
                "s####\n"
                "....#\n"
                "#####\n"
                "#...g\n"
            ),
            (
                "3 4\n"
                "s...\n"
                ".##.\n"
                "...g\n"
            ),
        ],
    )

    assert actual == (
        "[(Singular: H),"
        "(Singular: W),"
        "(Parallel: c | 0 to H-1)]"
    )


def test_numeric_grid_keeps_two_dimensions():
    actual = _predict(
        (
            "H W\n"
            "a_{0,0} a_{0,1} a_{0,W-1}\n"
            "a_{1,0} a_{1,1} a_{1,W-1}\n"
            ":\n"
            "a_{H-1,0} a_{H-1,1} a_{H-1,W-1}\n"
        ),
        [
            (
                "2 3\n"
                "1 2 3\n"
                "4 5 6\n"
            )
        ],
    )

    assert "TwoDimensional: a" in actual
