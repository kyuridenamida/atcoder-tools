import unittest
from atcodertools.fmtprediction.calculator import parse_to_calc_node, EvaluateError


class TestCalculator(unittest.TestCase):
    def test_parse_to_calc_node(self):
        self.assertEqual("N-(1-1)+1000*N*(N+1)",
                         str(parse_to_calc_node("N-(1-1)+1000*N*(N+1)")))

    def test_evaluate(self):
        self.assertEqual(1000, parse_to_calc_node(
            "N*(1+99)*(N-(1/N))/N").evaluate({"N": 10}))

        # Expect an error for the invalid input
        try:
            parse_to_calc_node("N").evaluate({"A": 10})
            self.fail("Must not reach here")
        except EvaluateError:
            pass

    def test_simplify(self):
        self.assertEqual("2*N", str(parse_to_calc_node("2*N-1+1").simplify()))
        self.assertEqual(
            "2*N", str(parse_to_calc_node("2*N-1+1-1+1-0").simplify()))


if __name__ == "__main__":
    unittest.main()
