from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
    _collapse_compact_digit_grid_rows,
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
            for sample_input in sample_inputs
        ],
        original_html="",
    )

    return str(
        predict_format(content).format
    )


def test_compact_digit_grid_rows_keep_outer_index():
    actual = _collapse_compact_digit_grid_rows(
        (
            "N\n"
            "a_1 a_2 ... a_9 a_{10}\n"
            "c_{11}c_{12}...c_{17}\n"
            "c_{21}c_{22}...c_{27}\n"
            "...\n"
            "...\n"
            "c_{N1}c_{N2}...c_{N7}\n"
        )
    )

    assert actual == (
        "N\n"
        "a_1 a_2 ... a_9 a_{10}\n"
        "c_{1}\n"
        "c_{2}\n"
        "...\n"
        "...\n"
        "c_{N}\n"
    )


def test_k2pc_easy_b_is_recovered():
    actual = _predict(
        (
            "N\n"
            "a_1 a_2 ... a_9 a_{10}\n"
            "c_{11}c_{12}...c_{17}\n"
            "c_{21}c_{22}...c_{27}\n"
            "...\n"
            "...\n"
            "c_{N1}c_{N2}...c_{N7}\n"
        ),
        [
            (
                "3\n"
                "1 1 2 1 1 1 1 1 1 3\n"
                "-X--X-X\n"
                "-------\n"
                "X--X-X-\n"
            ),
            (
                "2\n"
                "1 1 1 1 1 1 1 1 1 1\n"
                "XXXXXXX\n"
                "-------\n"
            ),
        ],
    )

    assert actual == (
        "[(Singular: N),"
        "(Parallel: a | 1 to 10),"
        "(Parallel: c | 1 to N)]"
    )


def test_space_separated_references_are_not_collapsed():
    actual = _collapse_compact_digit_grid_rows(
        (
            "N\n"
            "c_{11} c_{12} ... c_{17}\n"
        )
    )

    assert actual == (
        "N\n"
        "c_{11} c_{12} ... c_{17}\n"
    )


def test_single_index_vector_is_not_collapsed():
    actual = _collapse_compact_digit_grid_rows(
        (
            "N\n"
            "a_1 a_2 ... a_9 a_{10}\n"
        )
    )

    assert actual == (
        "N\n"
        "a_1 a_2 ... a_9 a_{10}\n"
    )
