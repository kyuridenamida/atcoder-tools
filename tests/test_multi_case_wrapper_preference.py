import unittest

from atcodertools.fmtprediction.predict_format import (
    MultiCaseFormatPrediction,
    _prefer_explicit_wrapper_candidates,
)


class _FakeVariable:
    def __init__(self, name, dimension):
        self.name = name
        self._dimension = dimension

    def dim_num(self):
        return self._dimension


class _FakeFormat:
    def __init__(self, text, variables):
        self._text = text
        self._variables = variables

    def __str__(self):
        return self._text

    def all_vars(self):
        return list(self._variables)


class TestMultiCaseWrapperPreference(
    unittest.TestCase
):
    def prediction(
        self,
        prefix,
        case,
        layout,
    ):
        return MultiCaseFormatPrediction(
            prefix,
            case,
            "T",
            {},
            layout,
        )

    def test_wrapper_beats_case_placeholder_split(
        self,
    ):
        count = _FakeVariable("T", 0)

        placeholder = _FakeVariable(
            "mathrmcase",
            1,
        )

        case = _FakeFormat(
            "[(Singular: N)]",
            [_FakeVariable("N", 0)],
        )

        wrapper = self.prediction(
            _FakeFormat(
                "[(Singular: T)]",
                [count],
            ),
            case,
            "wrapper",
        )

        split = self.prediction(
            _FakeFormat(
                (
                    "[(Singular: T),"
                    "(Parallel: mathrmcase "
                    "| 1 to T)]"
                ),
                [count, placeholder],
            ),
            case,
            "split",
        )

        self.assertEqual(
            [wrapper],
            _prefer_explicit_wrapper_candidates(
                [split, wrapper]
            ),
        )

    def test_real_split_array_is_preserved(
        self,
    ):
        count = _FakeVariable("T", 0)

        real_array = _FakeVariable(
            "A",
            1,
        )

        case = _FakeFormat(
            "[(Singular: N)]",
            [_FakeVariable("N", 0)],
        )

        wrapper = self.prediction(
            _FakeFormat(
                "[(Singular: T)]",
                [count],
            ),
            case,
            "wrapper",
        )

        split = self.prediction(
            _FakeFormat(
                (
                    "[(Singular: T),"
                    "(Parallel: A | 1 to T)]"
                ),
                [count, real_array],
            ),
            case,
            "split",
        )

        self.assertEqual(
            [split, wrapper],
            _prefer_explicit_wrapper_candidates(
                [split, wrapper]
            ),
        )


if __name__ == "__main__":
    unittest.main()
