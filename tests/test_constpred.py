import unittest
from logging import getLogger, DEBUG, Formatter, StreamHandler

from onlinejudge.service.atcoder import AtCoderProblem

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.constprediction.constants_prediction import predict_modulo, predict_constants, MultipleModCandidatesError
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler()
formatter = Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TestConstantsPrediction(unittest.TestCase):

    def setUp(self) -> None:
        self.client = AtCoderClient()

    def predict_constants(self, url: str) -> ProblemConstantSet:
        problem = AtCoderProblem.from_url(url)
        content = self.client.download_problem_content(problem)
        return predict_constants(content)

    def test_yes_no_prediction(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc008/tasks/agc008_d"), ProblemConstantSet(yes_str="Yes", no_str="No"))
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc010/tasks/agc010_a"), ProblemConstantSet(yes_str="YES", no_str="NO"))
        self.assertEqual(self.predict_constants("https://atcoder.jp/contests/agc002/tasks/agc002_c"),
                         ProblemConstantSet(yes_str="Possible", no_str="Impossible"))

    def test_modulo_prediction(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc005/tasks/agc005_d"), ProblemConstantSet(mod=924844033))
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc019/tasks/agc019_f"), ProblemConstantSet(mod=998244353))
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc012/tasks/agc012_d"), ProblemConstantSet(mod=1000000007))

    def test_no_prediction_results(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/arc001/tasks/arc001_2"), ProblemConstantSet())
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/abc038/tasks/abc038_c"), ProblemConstantSet())

    def test_modulo_prediction_fails_with_multi_mod_cands(self):
        html = "<p>101で割った余りを出力してください。もしくは n modulo 103を出力してください。</p>"
        with self.assertRaises(MultipleModCandidatesError):
            predict_modulo(ProblemContent(original_html=html))

    def test_case_only_with_no_str(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc001/tasks/agc001_d"), ProblemConstantSet(no_str="Impossible"))

    def test_tricky_mod_case_that_can_raise_multi_cands_error(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/abc103/tasks/abc103_c"), ProblemConstantSet())

    @unittest.expectedFailure
    def test_tricky_yes_no_case_difficult_to_recognize(self):
        # This test exists in order to demonstrate the current wrong behavior that doesn't detect some yes/no strings.
        # Please remove @unittest.expectedFailure when predict_yes_no() behaves correctly.

        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/abc110/tasks/abc110_b"), ProblemConstantSet(yes_str="War", no_str="No War"))

    @unittest.expectedFailure
    def test_modulo_prediction_failure(self):
        self.assertEqual(self.predict_constants(
            "https://atcoder.jp/contests/agc017/tasks/agc017_a"), ProblemConstantSet())


if __name__ == '__main__':
    unittest.main()
