#!/usr/bin/python3

import argparse
import os
from atcodertools.common.judgetype import NormalJudge, DecimalJudge, ErrorType,\
    JudgeType, NoJudgeTypeException, DEFAULT_EPS
from atcodertools.common.logging import logger
from atcodertools.tools.models.metadata import Metadata
from atcodertools.common.language import Language, ALL_LANGUAGES
from atcodertools.tools.codegen import main as codegen_main

USER_FACING_JUDGE_TYPE_LIST = [
    "normal", "absolute", "relative", "absolute_or_relative"]


def main(prog, args) -> None:
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

    parser.add_argument("--lang", '-l',
                        help="Programming language of your template code, {}.\n".format(
                            " or ".join([lang.name for lang in ALL_LANGUAGES])),
                        default=None)

    parser.add_argument("--dir", '-d',
                        help="Target directory to test. [Default] Current directory",
                        default=".")

    parser.add_argument("--without-login",
                        action="store_true",
                        help="Download data without login")

    args = parser.parse_args(args)

    old_metadata = Metadata.load_from(os.path.join(args.dir, "metadata.json"))

    # Use the old metadata as base metadata.
    output_metadata = Metadata.load_from(
        os.path.join(args.dir, "metadata.json"))

    old_metadata_judge_type = old_metadata.judge_method.judge_type.value

    if args.judge_type in ["absolute", "relative", "absolute_or_relative"]:
        new_metadata_judge_type = "decimal"
        output_metadata.judge_method.error_type = ErrorType(args.judge_type)
    elif args.judge_type is not None:
        new_metadata_judge_type = args.judge_type
    else:
        new_metadata_judge_type = old_metadata_judge_type

    if new_metadata_judge_type is not None and new_metadata_judge_type != old_metadata_judge_type:
        if new_metadata_judge_type == JudgeType.Normal.value:
            output_metadata.judge_method = NormalJudge()
        elif new_metadata_judge_type == JudgeType.Decimal.value:
            output_metadata.judge_method = DecimalJudge()
            if args.error_value is None:
                logger.warn(
                    "Error-value is not specified. DEFAULT_EPS is set")
                output_metadata.judge_method.diff = DEFAULT_EPS
        else:
            raise NoJudgeTypeException()

    if new_metadata_judge_type == JudgeType.Decimal.value and args.error_value is not None:
        output_metadata.judge_method.diff = args.error_value

    if args.lang is not None:
        if args.lang != output_metadata.lang.name:
            output_metadata.lang = Language.from_name(args.lang)
            output_metadata.code_filename = output_metadata.lang.get_code_filename(
                'main')
            url = "https://atcoder.jp/contests/{}/tasks/{}".format(
                output_metadata.problem.contest.contest_id, output_metadata.problem.problem_id)
            main_code_filename = os.path.join(
                args.dir, output_metadata.code_filename)
            if not os.path.exists(main_code_filename):
                a = ["--lang", output_metadata.lang.name, url]
                if args.without_login:
                    a.append("--without-login")
                codegen_main("", a, open(main_code_filename, 'w'))
            else:
                print("File exists: ", output_metadata.code_filename)
        else:
            print("Already set to {}. Skipping changing language...".format(args.lang))
    output_metadata.save_to(os.path.join(args.dir, "metadata.json"))
