import io

import json
import os
import pickle
import subprocess
import tempfile

from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.constprediction.constants_prediction import predict_constants, predict_modulo, predict_yes_no

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.fmtprediction.predict_format import FormatPredictor
from atcodertools.models.problem import Problem

atcoder = AtCoderClient()
CACHE_DIR = "./.cache/"

with open('./auto_generated/cpp/template_success.cpp') as f:
    TEMPLATE_CODE = f.read()


def get_and_set_cache(key, func):
    filepath = os.path.join(CACHE_DIR, key)
    if os.path.exists(os.path.join(CACHE_DIR, key)):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    res = func()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(res, f)
    return res


def get_contests():
    return atcoder.download_all_contests()


def get_problem_list(contest):
    def func():
        return atcoder.download_problem_list(contest)

    return get_and_set_cache("contest/{}".format(contest.contest_id), func)


def get_problem_content(problem: Problem):
    def func():
        return atcoder.download_problem_content(problem)

    return get_and_set_cache("problem/{}".format(problem.problem_id), func)


def norm_error(err):
    return str(type(err)).split(".")[-1][0:-2] if err is not None else None


class QualityResult:
    def __init__(self):
        self.problem = None
        self.contest = None
        self.statement_parse_error = None
        self.format_prediction_error = None
        self.prediction_result = None
        self.problem_content = None
        self.modulo = None
        self.modulo_error = None
        self.yes_str = None
        self.no_str = None
        self.codes = {}

    def build_dict(self):
        d = {}

        d["problem"] = self.problem.to_dict()

        d["contest"] = self.contest.to_dict()

        d["statement_parse"] = {
            "error": norm_error(self.statement_parse_error)
        }
        d["format_prediction"] = {
            "error": norm_error(self.format_prediction_error),
        }

        d["modulo"] = {
            "value": self.modulo,
            "error": norm_error(self.modulo_error)
        }
        d["yes_str"] = {
            "error": None,
            "value": self.yes_str
        }
        d["no_str"] = {
            "error": None,
            "value": self.no_str
        }

        d["codes"] = self.codes
        return d


def load_problem_content(result: QualityResult):
    try:
        result.problem_content = get_problem_content(result.problem)
    except Exception as e:
        result.statement_parse_error = e


def apply_clang(cpp: str):
    temp = tempfile.mktemp()
    with open(temp, 'w') as f:
        f.write(cpp)

    with open(temp, 'r') as f:
        out_data = subprocess.check_output(
            ["clang-format"], stdin=f, universal_newlines=True, timeout=100)
        return out_data


def predict_format(result: QualityResult):
    if result.problem_content is None:
        return None

    try:
        pred = FormatPredictor.predict(result.problem_content)
        result.prediction_result = pred
    except Exception as e:
        pred = None
        result.format_prediction_error = e

    if pred is not None:
        result.codes["cpp"] = apply_clang(CppCodeGenerator(TEMPLATE_CODE).generate_code(pred))


def do_predict_constants(result: QualityResult):
    if result.problem_content is None:
        return
    try:
        result.modulo = predict_modulo(result.problem_content.original_html)
    except Exception as e:
        result.modulo_error = e

    result.yes_str, result.no_str = predict_yes_no(result.problem_content.original_html)


def main():
    print("[")
    for contest in get_contests():
        problem_list = get_problem_list(contest)
        for problem in problem_list:
            result = QualityResult()
            result.contest = contest
            result.problem = problem
            load_problem_content(result)
            predict_format(result)
            do_predict_constants(result)
            print(json.dumps(result.build_dict(), indent=1), end="")
            print(", ")
    print("]")


if __name__ == "__main__":
    main()
