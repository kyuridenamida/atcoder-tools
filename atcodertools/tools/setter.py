#!/usr/bin/python3

import argparse
import os
import shutil
from atcodertools.common.judgetype import NormalJudge, DecimalJudge, ErrorType, MultiSolutionJudge, InteractiveJudge, JudgeType, NoJudgeTypeException, DEFAULT_EPS
from atcodertools.tools.models.metadata import Metadata
from atcodertools.common.language import Language, ALL_LANGUAGES
from atcodertools.tools.templates import get_default_judge_template_path
from atcodertools.tools.codegen import main as codegen_main

USER_FACING_JUDGE_TYPE_LIST = [
    "normal", "absolute", "relative", "absolute_or_relative", "multisolution", "interactive"]


def main(prog, args):
    if len(args) == 0:
        print("Usage: atcoder tools set [options]")
        return

    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--judge-type', '-j',
                        help='error type'
                             ' must be one of [{}]'.format(
                                 ', '.join(USER_FACING_JUDGE_TYPE_LIST)),
                        type=str,
                        default=None)

    parser.add_argument('--error-value', '-v',
                        help='error value for decimal number judge:'
                             ' [Default] ' + str(DEFAULT_EPS),
                        type=float,
                        default=None)

    parser.add_argument("--lang",
                        help="Programming language of your template code, {}.\n".format(
                            " or ".join([lang.name for lang in ALL_LANGUAGES])),
                        default=None)

    parser.add_argument("--dir", '-d',
                        help="Target directory to test. [Default] Current directory",
                        default=".")

    args = parser.parse_args(args)

    metadata = Metadata.load_from(args.dir + "/metadata.json")
    print(args.dir)

    new_judge_type = args.judge_type
    if new_judge_type in ["decimal", "absolute", "relative", "absolute_or_relative"]:
        new_judge_type = "decimal"
        if args.judge_type == "decimal":
            args.judge_type = "absolute_or_relative"

    old_judge_type = metadata.judge_method.judge_type.value

    if new_judge_type is not None and new_judge_type != old_judge_type:
        if new_judge_type == JudgeType.Normal.value:
            metadata.judge_method = NormalJudge()
        elif new_judge_type == JudgeType.Decimal.value:
            metadata.judge_method = DecimalJudge()
        elif new_judge_type == JudgeType.MultiSolution.value:
            metadata.judge_method = MultiSolutionJudge()
        elif new_judge_type == JudgeType.Interactive.value:
            metadata.judge_method = InteractiveJudge()
        else:
            raise NoJudgeTypeException()

    if new_judge_type == JudgeType.Decimal.value:
        if args.error_value is not None:
            metadata.judge_method.diff = args.error_value
        else:
            print("Warning: error-value is not specified default value is set. ")
        metadata.judge_method.error_type = ErrorType(args.judge_type)
    elif new_judge_type == JudgeType.MultiSolution.value:
        if not os.path.exists("./judge.cpp"):
            print("touch ./judge.cpp (multi sotlution)")
            judge_template_path = get_default_judge_template_path('cpp')
            shutil.copy(judge_template_path, "./judge.cpp")
        else:
            print("Judge Code exists")
    elif new_judge_type == JudgeType.Interactive.value:
        if not os.path.exists("/judge.cpp"):
            print("touch ./judge.cpp (interactive)")
            judge_template_path = get_default_judge_template_path('cpp')
            shutil.copy(judge_template_path, "./judge.cpp")
        else:
            print("Judge Code exists")

    if args.lang is not None:
        if args.lang != metadata.lang.name:
            metadata.lang = Language.from_name(args.lang)
            metadata.code_filename = metadata.lang.get_code_filename('main')
            url = "https://atcoder.jp/contests/{}/tasks/{}".format(
                metadata.problem.contest.contest_id, metadata.problem.problem_id)
            if not os.path.exists(metadata.code_filename):
                codegen_main("", ["--lang", metadata.lang.name,
                                  url], open(metadata.code_filename, 'w'))
            else:
                print("file exists: ", metadata.code_filename)
        else:
            print("already set to {}".format(args.lang))
    metadata.save_to(args.dir + "/metadata.json")
    return metadata
