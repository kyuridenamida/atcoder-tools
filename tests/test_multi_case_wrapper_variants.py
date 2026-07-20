\
from atcodertools.fmtprediction.multi_case_layout import (
    _extract_wrapper_prefix,
    _normalize_tex_atom,
)


def test_testcase_wrapper_with_spaced_indices_is_recognized():
    text = r"""
T
\mathrm{testcase} _ 1
\mathrm{testcase} _ 2
\vdots
\mathrm{testcase} _ T
"""

    assert _extract_wrapper_prefix(text) == "T\n"


def test_case_wrapper_accepts_ldots():
    text = r"""
T
\text{case}_1
\text{case}_2
\ldots
\text{case}_T
"""

    assert _extract_wrapper_prefix(text) == "T\n"


def test_unbraced_rm_and_hspace_wrapper():
    text = r"""
T
\rm case_1
\rm case_2
\hspace{9pt}\vdots
\rm case_T
"""

    assert _extract_wrapper_prefix(text) == "T\n"


def test_plain_tex_like_identifiers_are_preserved():
    assert _normalize_tex_atom("rm") == "rm"
    assert _normalize_tex_atom("it") == "it"
    assert _normalize_tex_atom("item") == "item"
    assert _normalize_tex_atom("iteration") == "iteration"
