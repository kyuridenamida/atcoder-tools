from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
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


def test_square_grid_uses_outer_index_structure():
    actual = _predict(
        (
            "H W\n"
            "s_{1, 1} s_{1, 2} "
            "... s_{1, W}\n"
            "s_{2, 1} s_{2, 2} "
            "... s_{2, W}\n"
            ":\n"
            "s_{H, 1} s_{H, 2} "
            "... s_{H, W}\n"
        ),
        [
            (
                "3 3\n"
                "#..\n"
                ".#.\n"
                "..#\n"
            )
        ],
    )

    assert actual == (
        "[(Singular: H),"
        "(Singular: W),"
        "(Parallel: s | 1 to H)]"
    )


def test_glued_square_grid_uses_outer_index():
    actual = _predict(
        (
            "H W K\n"
            "A_{1,1}A_{1,2}...A_{1,W}\n"
            ":\n"
            "A_{H,1}A_{H,2}...A_{H,W}\n"
        ),
        [
            (
                "3 3 2\n"
                "S..\n"
                ".#.\n"
                "..#\n"
            )
        ],
    )

    assert actual == (
        "[(Singular: H),"
        "(Singular: W),"
        "(Singular: K),"
        "(Parallel: A | 1 to H)]"
    )


def test_ldots_grid_becomes_string_rows():
    actual = _predict(
        (
            "H W\n"
            "a_{1, 1}\\ldotsa_{1, W}\n"
            ":\n"
            "a_{H, 1}\\ldotsa_{H, W}\n"
        ),
        [
            (
                "3 4\n"
                "...#\n"
                ".#..\n"
                "....\n"
            )
        ],
    )

    assert actual == (
        "[(Singular: H),"
        "(Singular: W),"
        "(Parallel: a | 1 to H)]"
    )


def test_numeric_grid_is_not_string_collapsed():
    actual = _predict(
        (
            "H W\n"
            "a_{1,1} a_{1,2} ... a_{1,W}\n"
            ":\n"
            "a_{H,1} a_{H,2} ... a_{H,W}\n"
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
