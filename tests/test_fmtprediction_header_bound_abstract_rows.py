from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import (
    predict_format,
)
from atcodertools.fmtprediction.tokenize_format import (
    collapse_string_runs,
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


def test_generic_i_row_is_still_removed():
    actual = collapse_string_runs(
        (
            "N\n"
            "S_1\n"
            "S_i\n"
            "S_N\n"
        )
    )

    assert actual == (
        "N\n"
        "S_1\n"
        "S_N\n"
    )


def test_declared_m_endpoint_is_preserved():
    actual = collapse_string_runs(
        (
            "n m Y Z\n"
            "c_1 p_1\n"
            "c_2 p_2\n"
            ":\n"
            ":\n"
            "c_m p_m\n"
            "b_1b_2 ‥‥ b_n\n"
        )
    )

    assert actual == (
        "n m Y Z\n"
        "c_1 p_1\n"
        "c_2 p_2\n"
        ":\n"
        ":\n"
        "c_m p_m\n"
        "b\n"
    )


def test_arc010_c_is_recovered():
    actual = _predict(
        (
            "n m Y Z\n"
            "c_1 p_1\n"
            "c_2 p_2\n"
            ":\n"
            ":\n"
            "c_m p_m\n"
            "b_1b_2 ‥‥ b_n\n"
        ),
        [
            (
                "5 3 3 5\n"
                "R 1\n"
                "G 1\n"
                "B 1\n"
                "RGBRR\n"
            ),
            (
                "3 3 3 5\n"
                "R 1\n"
                "G 1\n"
                "B 1\n"
                "RGB\n"
            ),
        ],
    )

    assert actual == (
        "[(Singular: n),"
        "(Singular: m),"
        "(Singular: Y),"
        "(Singular: Z),"
        "(Parallel: c,p | 1 to m),"
        "(Singular: b)]"
    )


def test_declared_r_grid_endpoint_is_preserved():
    actual = collapse_string_runs(
        (
            "r c\n"
            "C_{1,1}C_{1,2} ... C_{1,c}\n"
            ":\n"
            "C_{r,1}C_{r,2} ... C_{r,c}\n"
        )
    )

    assert actual == (
        "r c\n"
        "C_{1}\n"
        ":\n"
        "C_{r}\n"
    )


def test_soundhound_grid_is_recovered():
    actual = _predict(
        (
            "r c\n"
            "C_{1,1}C_{1,2} ... C_{1,c}\n"
            ":\n"
            "C_{r,1}C_{r,2} ... C_{r,c}\n"
        ),
        [
            (
                "3 3\n"
                "...\n"
                "...\n"
                "...\n"
            ),
            (
                "2 4\n"
                "abcd\n"
                "efgh\n"
            ),
        ],
    )

    assert actual == (
        "[(Singular: r),"
        "(Singular: c),"
        "(Parallel: C | 1 to r)]"
    )
