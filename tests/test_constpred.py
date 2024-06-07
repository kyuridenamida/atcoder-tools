import os
import tempfile
import unittest
from logging import getLogger, DEBUG, Formatter, StreamHandler

from atcodertools.common.judgetype import JudgeType, ErrorType
from atcodertools.constprediction.constants_prediction import predict_constants, predict_modulo, \
    predict_yes_no, YesNoPredictionFailedError, predict_judge_method, \
    MultipleDecimalCandidatesError, predict_limit, \
    predict_is_format_analysis_allowed_by_rule
from tests.utils.gzip_controller import make_html_data_controller

ANSWER_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    './resources/test_constpred/answer.txt')

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler()
formatter = Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def _to_str(x):
    if x is None:
        return ""
    return str(x)


class TestConstantsPrediction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.html_data_controller = make_html_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.html_data_controller.create_dir()

    def tearDown(self):
        self.html_data_controller.remove_dir()

    def test_predict_constants(self):
        with open(ANSWER_FILE, 'r') as f:
            answers = f.read().split("\n")

        agc_html_paths = [path for path in sorted(
            os.listdir(self.test_dir)) if "agc" in path]
        for html_path, answer_line in zip(agc_html_paths, answers):
            logger.debug("Testing {}".format(html_path))
            constants = predict_constants(self._load(html_path))
            output_line = "{:40} [mod]{:10} [yes]{:10} [no]{:10}".format(html_path.split(".")[0],
                                                                         _to_str(
                                                                             constants.mod),
                                                                         _to_str(
                                                                             constants.yes_str),
                                                                         _to_str(constants.no_str))
            self.assertEqual(answer_line.rstrip(), output_line.rstrip())

    def test_yes_no_prediction_fails_when_failing_to_parse_html(self):
        try:
            predict_yes_no("broken html")
            self.fail("Must not reach here")
        except YesNoPredictionFailedError:
            pass

    def test_case_only_with_no_str(self):
        yes_str, no_str = predict_yes_no(self._load("agc001-D.html"))
        self.assertEqual(None, yes_str)
        self.assertEqual("Impossible", no_str)

    def test_predict_time_limit(self):
        timeout = predict_limit(self._load("dwacon2017-prelims-A.html"))
        self.assertEqual(timeout, 2525)
        timeout = predict_limit(self._load("dwacon2017-prelims-E.html"))
        self.assertEqual(timeout, 5252)

    @unittest.expectedFailure
    def test_tricky_mod_case_that_can_raise_multi_cands_error(self):
        # This test exists in order to demonstrate the current wrong behavior that throws MultipleModCandidatesError.
        # None is the true answer for ABC103-C. This test shouldn't fail with a better prediction method.
        # Please remove @unittest.expectedFailure when predict_modulo() behaves
        # correctly.

        modulo = predict_modulo(self._load("abc103-C.html"))
        self.assertIsNone(modulo)

    @unittest.expectedFailure
    def test_tricky_yes_no_case_difficult_to_recognize(self):
        # This test exists in order to demonstrate the current wrong behavior that doesn't detect some yes/no strings.
        # Please remove @unittest.expectedFailure when predict_yes_no() behaves
        # correctly.

        yes_str, no_str = predict_yes_no(self._load("abc110-B.html"))
        self.assertEqual("War", yes_str)
        self.assertEqual("No War", no_str)

    def test_relative_or_absolute_error_judge_method_case(self):
        judge_method = predict_judge_method(
            """
            <section>
            <h3>出力</h3><p><var>\\frac{1}{\\frac{1}{A_1} + \ldots + \\frac{1}{A_N}}</var> の値を表す小数 (または整数) を出力せよ。</p>
            <p>出力は、ジャッジの出力との絶対誤差または相対誤差が <var>10^{-5}</var> 以下のとき正解と判定される。</p>
            </section>""")
        self.assertEqual(0.00001, judge_method.to_dict()["diff"])
        self.assertEqual(JudgeType.Decimal.value,
                         judge_method.to_dict()["judge_type"])
        self.assertEqual(ErrorType.AbsoluteOrRelative.value,
                         judge_method.to_dict()["error_type"])

    def test_absolute_error_judge_method_case(self):
        judge_method = predict_judge_method(
            """
            <div class="part">
                <h3>出力</h3>
                <section>
                    入力に基づいて逆算した 体重 <var>[kg]</var> を一行に出力せよ。<br />
                    出力は絶対誤差が <var>10^{−2}</var> 以下であれば許容される。<br />
                    なお、出力の最後には改行を入れること。
                </section>
            </div>""")
        self.assertEqual(0.01, judge_method.to_dict()["diff"])
        self.assertEqual(JudgeType.Decimal.value,
                         judge_method.to_dict()["judge_type"])
        self.assertEqual(ErrorType.Absolute.value,
                         judge_method.to_dict()["error_type"])

    def test_relative_error_judge_method_case(self):
        judge_method = predict_judge_method(
            """
            <div class="part">
            <section>
            <h3>出力</h3><p>すべての寿司が無くなるまでの操作回数の期待値を出力せよ。
            相対誤差が <var>10^{-9}</var> 以下ならば正解となる。</p>
            </section>
            </div>
            </div>""")
        self.assertEqual(0.000000001, judge_method.to_dict()["diff"])
        self.assertEqual(JudgeType.Decimal.value,
                         judge_method.to_dict()["judge_type"])
        self.assertEqual(ErrorType.Relative.value,
                         judge_method.to_dict()["error_type"])

    def test_normal_judge_method_case(self):
        judge_method = predict_judge_method(
            """
            <div class="part">
            <section>
            <h3>出力</h3><p><var>N!</var> の正の約数の個数を <var>10^9+7</var> で割った余りを出力せよ。</p>
            </section>
            </div>
            </div>""")
        self.assertEqual(JudgeType.Normal.value,
                         judge_method.to_dict()["judge_type"])

    def test_judge_method_prediction_fails_with_multiple_cands(self):
        try:
            predict_judge_method(
                "<var>10^{-6}</var> もしくは <var>10^{-5}</var>以下の相対誤差")
            self.fail("Must not reach here")
        except MultipleDecimalCandidatesError:
            pass

    @unittest.expectedFailure
    def test_tricky_judge_method_case(self):
        # This test exists in order to demonstrate the current wrong behavior that detects unrelated mention wrongly.
        # Please remove @unittest.expectedFailure when predict_judge_method() behaves
        # correctly.
        judge_method = predict_judge_method(
            """
            <div class="part">
            <section>
            <h3>問題文</h3><p><var>N</var> 人のクラスがあり、色 <var>1,2,...,M</var> の中から <var>1</var> つの色を選んでテーマカラーを決めることとなりました。</p>
            <p>それぞれの人が同確率でどれかの色 <var>1</var> つに投票するとき、色 <var>i(1 \leq i \leq M)</var> に <var>r_i</var> 票集まる確率を <var>p</var> とします。</p>
            <p><var>p \geq 10^{-x}</var> を満たす最小の整数 <var>x</var> を求めてください。</p>
            <p>ただし、<var>p</var> に <var>10^{-6}</var> 以下の相対誤差が生じても <var>x</var> は変わらないことが保証されるものとします。</p>
            </section>
            </div>""")
        self.assertEqual(JudgeType.Normal.value,
                         judge_method.to_dict()["judge_type"])

    def test_predict_format_analysis_allowed_by_rule_with_finished_abc(self):
        is_format_analysis_allowed_by_rule = predict_is_format_analysis_allowed_by_rule(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta property="og:url" content="https://atcoder.jp/contests/abc352/tasks/abc352_d" />
            </head>
            <div class="row">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="/contests/abc352/tasks"><span class="glyphicon glyphicon-tasks" aria-hidden="true"></span> 問題</a></li>
                    <li><a href="/contests/abc352/standings/virtual"><span class="glyphicon glyphicon-sort-by-attributes-alt" aria-hidden="true"></span> バーチャル順位表</a></li>
                </ul>
            </div>
            </body>
            </html>
            """)
        self.assertEqual(True, is_format_analysis_allowed_by_rule)

    def test_predict_format_analysis_allowed_by_rule_with_ongoing_abc(self):
        is_format_analysis_allowed_by_rule = predict_is_format_analysis_allowed_by_rule(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta property="og:url" content="https://atcoder.jp/contests/abc352/tasks/abc352_d" />
            </head>
            <div class="row">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="/contests/abc352/tasks"><span class="glyphicon glyphicon-tasks" aria-hidden="true"></span> 問題</a></li>
                </ul>
            </div>
            </body>
            </html>
            """)
        self.assertEqual(False, is_format_analysis_allowed_by_rule)

    def test_predict_format_analysis_allowed_by_rule_with_ongoing_arc(self):
        is_format_analysis_allowed_by_rule = predict_is_format_analysis_allowed_by_rule(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta property="og:url" content="https://atcoder.jp/contests/arc352/tasks/arc352_a" />
            </head>
            <div class="row">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="/contests/arc352/tasks"><span class="glyphicon glyphicon-tasks" aria-hidden="true"></span> 問題</a></li>
                </ul>
            </div>
            </body>
            </html>
            """)
        self.assertEqual(True, is_format_analysis_allowed_by_rule)

    def _load(self, html_path):
        with open(os.path.join(self.test_dir, html_path), 'r') as f:
            return f.read()


if __name__ == '__main__':
    unittest.main()
