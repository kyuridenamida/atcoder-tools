import asyncio
import json
import os
import pickle
import subprocess
import sys
import tempfile
import threading

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.client.models.problem import Problem
from atcodertools.client.models.problem_content import InputFormatDetectionError, SampleDetectionError, ProblemContent
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.common.language import RUST, CPP, JAVA, PYTHON, DLANG, NIM, CSHARP
from atcodertools.constprediction.constants_prediction import predict_modulo, predict_yes_no, predict_judge_method
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.fileutils.load_text_file import load_text_file
from atcodertools.fmtprediction.predict_format import predict_format as predict

atcoder = AtCoderClient()
CACHE_DIR = "./.cache/"


class Skipped(Exception):
    pass


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
        print("downloading problem list ...", file=sys.stderr)
        return atcoder.download_problem_list(contest)

    return get_and_set_cache("contest/{}".format(contest.contest_id), func)


def get_problem_content(problem: Problem):
    def func():
        print("downloading html ...", file=sys.stderr)
        raw_response = atcoder._request(problem.get_url())
        return raw_response.text

    return ProblemContent.from_html(get_and_set_cache("problem/{}".format(problem.problem_id), func))


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
        self.yes_str_error = None
        self.no_str_error = None
        self.codes = {}
        self.constant_set = None
        self.judge_method = None
        self.judge_method_error = None

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
            "error": norm_error(self.yes_str_error),
            "value": self.yes_str
        }
        d["no_str"] = {
            "error": norm_error(self.no_str_error),
            "value": self.no_str
        }
        d["judge_method"] = {
            "error": norm_error(self.judge_method_error),
            "value": self.judge_method
        }
        d["codes"] = self.codes
        return d


def load_problem_content(result: QualityResult):
    try:
        result.problem_content = get_problem_content(result.problem)
    except (SampleDetectionError, InputFormatDetectionError) as e:
        result.statement_parse_error = e


def apply_clang(cpp: object) -> object:
    temp = tempfile.mktemp()
    with open(temp, 'w') as f:
        f.write(cpp)

    with open(temp, 'r') as f:
        out_data = subprocess.check_output(
            ["clang-format"], stdin=f, universal_newlines=True, timeout=100)
        return out_data


def predict_format(result: QualityResult):
    if result.problem_content is None:
        result.format_prediction_error = Skipped()
        return

    try:
        pred = predict(result.problem_content, True)
        result.prediction_result = pred
    except Exception as e:
        result.format_prediction_error = e


def do_predict_constants(result: QualityResult):
    if result.problem_content is None or result.problem_content.original_html is None:
        result.modulo_error = Skipped()
        result.yes_str_error = Skipped()
        result.no_str_error = Skipped()
        result.constant_set = ProblemConstantSet()
        return
    try:
        result.modulo = predict_modulo(result.problem_content.original_html)
    except Exception as e:
        result.modulo_error = e

    result.yes_str, result.no_str = predict_yes_no(
        result.problem_content.original_html)

    judge_method = None
    try:
        judge_method = predict_judge_method(
            result.problem_content.original_html)
        if judge_method is not None:
            result.judge_method = judge_method.to_dict()

    except Exception as e:
        result.judge_method_error = e

    result.constant_set = ProblemConstantSet(
        mod=result.modulo,
        yes_str=result.yes_str,
        no_str=result.no_str,
        judge_method=judge_method
    )


CPP_TEMPLATE = load_text_file(CPP.default_template_path)
JAVA_TEMPLATE = load_text_file(JAVA.default_template_path)
RUST_TEMPLATE = load_text_file(RUST.default_template_path)
PYTHON_TEMPLATE = load_text_file(PYTHON.default_template_path)
D_TEMPLATE = load_text_file(DLANG.default_template_path)
NIM_TEMPLATE = load_text_file(NIM.default_template_path)
CSHARP_TEMPLATE = load_text_file(CSHARP.default_template_path)


def generate_code(result: QualityResult):
    if result.prediction_result is None:
        result_format = None
    else:
        result_format = result.prediction_result.format

    result.codes["cpp"] = apply_clang(CPP.default_code_generator(CodeGenArgs(
        CPP_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=CPP.name)
    )))
    result.codes["java"] = JAVA.default_code_generator(CodeGenArgs(
        JAVA_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=JAVA.name)
    ))
    result.codes["rust"] = RUST.default_code_generator(CodeGenArgs(
        RUST_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=RUST.name)
    ))
    result.codes["python"] = PYTHON.default_code_generator(CodeGenArgs(
        PYTHON_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=PYTHON.name)
    ))
    result.codes["d"] = DLANG.default_code_generator(CodeGenArgs(
        D_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=DLANG.name)
    ))
    result.codes["nim"] = NIM.default_code_generator(CodeGenArgs(
        NIM_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=NIM.name)
    ))
    result.codes["csharp"] = CSHARP.default_code_generator(CodeGenArgs(
        CSHARP_TEMPLATE,
        result_format,
        result.constant_set,
        CodeStyleConfig(lang=CSHARP.name)
    ))


_counter = 0
_lock = threading.Lock()


def increment_counter():
    global _counter
    with _lock:
        _counter += 1


def get_counter():
    global _counter
    with _lock:
        return _counter


async def process_problem(problem, contest, total) -> QualityResult:
    try:
        result = QualityResult()
        result.contest = contest
        result.problem = problem
        load_problem_content(result)
        predict_format(result)
        do_predict_constants(result)
        generate_code(result)
        increment_counter()
        print("Processed {} ... {}/{}".format(
            problem.problem_id, get_counter(), total), file=sys.stderr)
        return result
    except Exception as e:
        print(e, file=sys.stderr)
        for task in asyncio.Task.all_tasks():
            task.cancel()


def main(output_path: str):
    loop = asyncio.get_event_loop()
    contests = get_contests()

    args_list = []
    for idx, contest in enumerate(contests):
        problem_list = get_problem_list(contest)
        print("Add {} ... ({}/{})".format(
            contest.contest_id,
            idx,
            len(contests)
        ), file=sys.stderr)

        args_list += [dict(
            problem=problem,
            contest=contest
        ) for problem in problem_list]
    # args_list = args_list[:100]
    tasks = asyncio.wait([process_problem(**args, total=len(args_list))
                          for idx, args in enumerate(args_list)])
    done, pending = loop.run_until_complete(tasks)
    done = [x.result() for x in done]
    res = []

    for result in done:
        res.append(result.build_dict())
    loop.close()

    json_str = json.dumps(res)

    with open(output_path, "w") as fp:
        fp.write(json_str)


if __name__ == "__main__":
    main("./out/all_data.json")
