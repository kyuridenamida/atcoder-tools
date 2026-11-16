#!/usr/bin/python3

import argparse
import os
import shutil

from atcodertools.common.judgetype import (
    DEFAULT_EPS,
    DecimalJudge,
    ErrorType,
    InteractiveJudge,
    JudgeType,
    MultiSolutionJudge,
    NoJudgeTypeException,
    NormalJudge,
)
from atcodertools.common.language import ALL_LANGUAGES, Language
from atcodertools.common.logging import logger
from atcodertools.tools.codegen import main as codegen_main
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.templates import get_default_judge_template_path

USER_FACING_JUDGE_TYPE_LIST = ["normal", "absolute", "relative", "absolute_or_relative", "multisolution", "interactive"]


def main(prog: str, args: list[str]) -> None:
    if len(args) == 0:
        print("Usage: atcoder tools set [options]")
        return

    parser = argparse.ArgumentParser(prog=prog, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "--judge-type",
        "-j",
        help="error type must be one of [{}]".format(", ".join(USER_FACING_JUDGE_TYPE_LIST)),
        type=str,
        default=None,
    )

    parser.add_argument(
        "--error-value",
        "-v",
        help="error value for decimal number judge: [Default] " + str(DEFAULT_EPS),
        type=float,
        default=None,
    )

    parser.add_argument(
        "--lang",
        help="Programming language of your template code, {}.\n".format(
            " or ".join([lang.name for lang in ALL_LANGUAGES])
        ),
        default=None,
    )

    parser.add_argument("--dir", "-d", help="Target directory to test. [Default] Current directory", default=".")

    parsed_args = parser.parse_args(args)

    old_metadata = Metadata.load_from(os.path.join(parsed_args.dir, "metadata.json"))

    # Use the old metadata as base metadata.
    output_metadata = Metadata.load_from(os.path.join(parsed_args.dir, "metadata.json"))

    if parsed_args.judge_type in ["absolute", "relative", "absolute_or_relative"]:
        new_metadata_judge_type = "decimal"
    else:
        new_metadata_judge_type = parsed_args.judge_type

    old_metadata_judge_type = old_metadata.judge_method.judge_type.value

    if new_metadata_judge_type is not None and new_metadata_judge_type != old_metadata_judge_type:
        if new_metadata_judge_type == JudgeType.Normal.value:
            output_metadata.judge_method = NormalJudge()
        elif new_metadata_judge_type == JudgeType.Decimal.value:
            output_metadata.judge_method = DecimalJudge()
        elif new_metadata_judge_type == JudgeType.MultiSolution.value:
            output_metadata.judge_method = MultiSolutionJudge()
        elif new_metadata_judge_type == JudgeType.Interactive.value:
            output_metadata.judge_method = InteractiveJudge()
        else:
            raise NoJudgeTypeException()

    judge_code_filename = os.path.join(parsed_args.dir, "judge.cpp")

    if new_metadata_judge_type == JudgeType.Decimal.value:
        assert isinstance(output_metadata.judge_method, DecimalJudge)
        if parsed_args.error_value is not None:
            output_metadata.judge_method.diff = parsed_args.error_value
        else:
            logger.warning("Error-value is not specified. Default value will be set.")
        output_metadata.judge_method.error_type = ErrorType(parsed_args.judge_type)

    elif new_metadata_judge_type == JudgeType.MultiSolution.value:
        if not os.path.exists(judge_code_filename):
            print(f"Creating {judge_code_filename} (multi-solution)")
            judge_template_path = get_default_judge_template_path("cpp")
            shutil.copy(judge_template_path, judge_code_filename)
        else:
            print("Judge code exists. Skipping creating judge code...")
    elif new_metadata_judge_type == JudgeType.Interactive.value:
        if not os.path.exists(judge_code_filename):
            print(f"Creating {judge_code_filename} (interactive)")
            judge_template_path = get_default_judge_template_path("cpp")
            shutil.copy(judge_template_path, judge_code_filename)
        else:
            print("Judge code exists. Skipping creating judge code...")

    if parsed_args.lang is not None:
        assert output_metadata.lang is not None and output_metadata.problem is not None
        if parsed_args.lang != output_metadata.lang.name:
            output_metadata.lang = Language.from_name(parsed_args.lang)
            output_metadata.code_filename = output_metadata.lang.get_code_filename("main")
            url = f"https://atcoder.jp/contests/{output_metadata.problem.contest.contest_id}/tasks/{output_metadata.problem.problem_id}"
            main_code_filename = os.path.join(parsed_args.dir, output_metadata.code_filename)
            if not os.path.exists(main_code_filename):
                with open(main_code_filename, "w") as f:
                    codegen_main("", ["--lang", output_metadata.lang.name, url], f)
            else:
                print("File exists: ", output_metadata.code_filename)
        else:
            print(f"Already set to {parsed_args.lang}. Skipping changing language...")
    output_metadata.save_to(os.path.join(parsed_args.dir, "metadata.json"))
