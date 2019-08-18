import logging
import unittest
from typing import Any, Optional, Dict

from onlinejudge.service.atcoder import AtCoderProblem

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.fmtprediction.predict_format import predict_format, NoPredictionResultError


fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)


class TestFormatPrediction(unittest.TestCase):

    def setUp(self) -> None:
        self.client = AtCoderClient()

    def predict_format(self, url: str) -> Optional[Dict[str, Any]]:
        problem = AtCoderProblem.from_url(url)
        content = self.client.download_problem_content(problem)
        try:
            result = predict_format(content)
            print(result.format)
            return {
                'format': str(result.format),
                'type': {var.name: var.type.to_py_type() for var in result.format.all_vars()},
            }
        except NoPredictionResultError:
            return None

    def test_variables_with_long_names(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/arc001/tasks/arc001_4"), {
            'format': '[(Singular: N),(Singular: start),(Singular: goal),(Parallel: l,r | 0 to N)]',
            'type': {'N': int, 'start': int, 'goal': int, 'l': int, 'r': int},
        })

    def test_an_old_problem(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/abc002/tasks/abc002_2"), {
            'format': '[(Singular: W)]',
            'type': {'W': str},
        })

    def test_parallel_to_2n(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/agc001/tasks/agc001_a"), {
            'format': '[(Singular: N),(Parallel: L | 1 to 2*N)]',
            'type': {'N': int, 'L': int},
        })

    def test_parallel_from_1_to_1(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/agc007/tasks/agc007_c"), {
            'format': '[(Singular: N),(Parallel: d | 1 to 1),(Singular: x)]',
            'type': {'N': int, 'd': int, 'x': int},
        })

    def test_parallel_with_two_variables(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/agc015/tasks/agc015_e"), {
            'format': '[(Singular: N),(Parallel: X,V | 1 to N)]',
            'type': {'N': int, 'X': int, 'V': int},
        })

    def test_matrix_of_char(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/agc028/tasks/agc028_f"), {
            'format': '[(Singular: N),(Parallel: A | 1 to N)]',
            'type': {'N': int, 'A': str},
        })

    @unittest.expectedFailure
    def test_matrix_of_char_failure(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/agc004/tasks/agc004_c"))

    @unittest.expectedFailure
    def test_long_digits(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/arc088/tasks/arc088_b"), {
            'format': '[(Singular: S)]',
            'type': {'S': str},
        })

    def test_float_type(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/arc015/tasks/arc015_4"), {
            'format': '[(Singular: T),(Singular: N),(Singular: P),(Parallel: q,x,t | 1 to N)]',
            'type': {'T': int, 'N': int, 'P': float, 'q': float, 'x': int, 't': int},
        })

    def test_char_indexed(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/agc008/tasks/agc008_c"), {
            'format': '[(Singular: a_I),(Singular: a_O),(Singular: a_T),(Singular: a_J),(Singular: a_L),(Singular: a_S),(Singular: a_Z)]',
            'type': {'a_I': int, 'a_O': int, 'a_T': int, 'a_J': int, 'a_L': int, 'a_S': int, 'a_Z': int},
        })

    @unittest.expectedFailure
    def test_array_of_char_without_spaces(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/arc097/tasks/arc097_d"), None)

    @unittest.expectedFailure
    def test_two_steps_parallel(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/arc096/tasks/arc096_d"), None)

    @unittest.expectedFailure
    def test_not_space_separated(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/arc002/tasks/arc002_2"))

    @unittest.expectedFailure
    def test_complicated_input_format(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/agc029/tasks/agc029_f"))

    @unittest.expectedFailure
    def test_two_pre_tags(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/agc027/tasks/agc027_f"))

    def test_complicated_variable_names(self) -> None:
        self.assertEqual(self.predict_format("https://atcoder.jp/contests/abc022/tasks/abc022_d"), {
            'format': '[(Singular: N),(Parallel: Ax,Ay | 1 to N),(Parallel: Bx,By | 1 to N)]',
            'type': {'N': int, 'Ax': int, 'Ay': int, 'Bx': int, 'By': int},
        })

    @unittest.expectedFailure
    def test_lists_with_heterogeneous_lengths(self) -> None:
        self.assertIsNotNone(self.predict_format(
            "https://atcoder.jp/contests/iroha2019-day1/tasks/iroha2019_day1_k"))


if __name__ == "__main__":
    unittest.main()
