#!/usr/bin/python3
import argparse
import glob
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any, Optional

from colorama import Fore

from atcodertools.common.judgetype import DEFAULT_EPS as DEFAULT_EPS
from atcodertools.common.judgetype import (
    DecimalJudge,
    ErrorType,
    InteractiveJudge,
    Judge,
    MultiSolutionJudge,
    NormalJudge,
)
from atcodertools.common.language import Language
from atcodertools.common.logging import logger
from atcodertools.config.config import USER_CONFIG_PATH, get_config
from atcodertools.executils.run_program import ExecResult, ExecStatus, run_interactive_program, run_program
from atcodertools.tools import get_default_config_path
from atcodertools.tools.compiler import BadStatusCodeException, compile_main_and_judge_programs
from atcodertools.tools.models.metadata import DEFAULT_METADATA, Metadata
from atcodertools.tools.utils import with_color


class NoExecutableFileError(Exception):
    pass


class IrregularSampleFileError(Exception):
    pass


class InvalidJudgeTypeError(Exception):
    pass


class TestSummary:
    # Not a pytest test class; prevent pytest collection warnings.
    __test__ = False

    def __init__(self, success_count: int, has_error_output: bool) -> None:
        self.success_count = success_count
        self.has_error_output = has_error_output

    def __eq__(self, other: Any) -> bool:
        return bool(self.success_count == other.success_count and self.has_error_output == other.has_error_output)


def is_executable_file(file_name: str) -> bool:
    if platform.system() == "Windows":
        return any(
            re.match(rf"^.*\{ext}$", file_name, re.IGNORECASE)
            for ext in os.environ.get("PATHEXT", default="").split(";")
        )
    else:
        return (
            os.access(file_name, os.X_OK)
            and Path(file_name).is_file()
            and file_name.find(".cpp") == -1
            and not file_name.endswith(".txt")
        )  # cppやtxtを省くのは一応の Cygwin 対策


def infer_exec_file(filenames: list[str], excluded_exec_files: list[str]) -> str:
    exec_files = [name for name in sorted(filenames) if is_executable_file(name) and (name not in excluded_exec_files)]

    if len(exec_files) == 0:
        raise NoExecutableFileError
    else:
        exec_file = exec_files[0]
    if len(exec_files) >= 2:
        logger.warning(
            "{}  {}".format(
                f"There're multiple executable files. '{exec_file}' is selected.",
                f"The candidates were {exec_files}.",
            )
        )
    return exec_file


def infer_case_num(sample_filename: str) -> int:
    sample_basename = os.path.basename(sample_filename)
    result = ""
    for c in sample_basename:
        if c.isdigit():
            result += c
    if result == "":
        raise IrregularSampleFileError(f"Cannot infer case number from file name: {sample_filename}")
    return int(result)


def build_details_str(exec_res: ExecResult, input_file: str, output_file: str) -> str:
    res = ""

    def append(text: str, end: str = "\n") -> None:
        nonlocal res
        res += text + end

    with open(output_file) as f:
        expected_output = f.read()

    append(with_color("[Input]", Fore.LIGHTMAGENTA_EX))
    with open(input_file) as f:
        append(f.read(), end="")

    append(with_color("[Expected]", Fore.LIGHTMAGENTA_EX))
    append(expected_output, end="")
    if exec_res.judge_message is not None and exec_res.judge_message != "":
        append("judge message: " + exec_res.judge_message)

    append(with_color("[Received]", Fore.LIGHTMAGENTA_EX))
    append(exec_res.output or "", end="")

    if exec_res.status != ExecStatus.NORMAL:
        append(with_color(f"Aborted ({exec_res.status.name})\n", Fore.LIGHTYELLOW_EX))

    if exec_res.has_stderr():
        append(with_color("[Error]", Fore.LIGHTYELLOW_EX))
        append(exec_res.stderr or "", end="")
    return res


def run_for_samples(
    exec_file: str,
    sample_pair_list: list[tuple[str, str]],
    timeout_sec: int,
    judge_method: Judge = NormalJudge(),  # noqa: B008
    knock_out: bool = False,
    skip_io_on_success: bool = False,
    cwd: str = "./",
    judge_program_language: Optional[Language] = None,
) -> TestSummary:
    success_count = 0
    has_error_output = False
    for in_sample_file, out_sample_file in sample_pair_list:
        if isinstance(judge_method, InteractiveJudge):
            assert judge_program_language is not None
            exec_res = run_interactive_program(
                exec_file,
                judge_program_language.get_test_command("judge", cwd),
                in_sample_file,
                out_sample_file,
                timeout_sec=timeout_sec,
                current_working_dir=cwd,
            )
            is_correct = exec_res.is_correct_output(judge_method=judge_method)
        else:
            # Run program
            exec_res = run_program(exec_file, in_sample_file, timeout_sec=timeout_sec, current_working_dir=cwd)

            if isinstance(judge_method, MultiSolutionJudge):
                is_correct = exec_res.is_correct_output(
                    sample_input_file=in_sample_file,
                    sample_output_file=out_sample_file,
                    cwd=cwd,
                    judge_method=judge_method,
                    judge_program_language=judge_program_language,
                )
            else:
                # Output header
                with open(out_sample_file) as f:
                    expected_answer_text = f.read()

                is_correct = exec_res.is_correct_output(expected_answer_text, judge_method)

        if exec_res.output is None:
            exec_res.output = ""
        if exec_res.stderr is None:
            exec_res.stderr = ""

        has_error_output = has_error_output or exec_res.has_stderr()

        if is_correct:
            if exec_res.has_stderr():
                message = with_color("CORRECT but with stderr (Please remove stderr!)", Fore.LIGHTYELLOW_EX)
            else:
                message = "{} {elapsed} ms".format(
                    with_color("PASSED", Fore.LIGHTGREEN_EX), elapsed=exec_res.elapsed_ms
                )
            success_count += 1
        else:
            if exec_res.status == ExecStatus.NORMAL:
                message = with_color("WA", Fore.LIGHTRED_EX)
            else:
                message = with_color(exec_res.status.name, Fore.LIGHTYELLOW_EX)

        print(f"# {os.path.basename(in_sample_file)} ... {message}")

        # Output details for incorrect results or has stderr.
        if not is_correct or (exec_res.has_stderr() and not skip_io_on_success):
            print(f"{build_details_str(exec_res, in_sample_file, out_sample_file)}\n")

        if knock_out and not is_correct:
            print("Stop testing ...")
            break
    return TestSummary(success_count, has_error_output)


def validate_sample_pair(in_sample_file: str, out_sample_file: str) -> None:
    if infer_case_num(in_sample_file) != infer_case_num(out_sample_file):
        logger.error(f"The file combination of {in_sample_file} and {out_sample_file} is wrong.")
        raise IrregularSampleFileError


def run_single_test(
    exec_file: str,
    in_sample_file_list: list[str],
    out_sample_file_list: list[str],
    timeout_sec: int,
    case_num: int,
    judge_method: Judge,
    cwd: str,
    judge_program_language: Optional[Language],
) -> bool:
    def single_or_none(lst: list[str]) -> Optional[str]:
        if len(lst) == 1:
            return lst[0]
        if len(lst) == 0:
            return None
        raise IrregularSampleFileError(f"Multiple samples are detected for given case num: {lst}")

    in_sample_file = single_or_none([name for name in in_sample_file_list if infer_case_num(name) == case_num])
    out_sample_file = single_or_none([name for name in out_sample_file_list if infer_case_num(name) == case_num])

    if in_sample_file is None or out_sample_file is None:
        print(f"Invalid test case number: {case_num}")
        return False

    validate_sample_pair(in_sample_file, out_sample_file)

    test_summary = run_for_samples(
        exec_file,
        [(in_sample_file, out_sample_file)],
        timeout_sec,
        judge_method,
        cwd=cwd,
        judge_program_language=judge_program_language,
    )

    return test_summary.success_count == 1 and not test_summary.has_error_output


def run_all_tests(
    exec_file: str,
    in_sample_file_list: list[str],
    out_sample_file_list: list[str],
    timeout_sec: int,
    knock_out: bool,
    skip_stderr_on_success: bool,
    judge_method: Judge,
    cwd: str,
    judge_program_language: Optional[Language],
) -> bool:
    if len(in_sample_file_list) != len(out_sample_file_list):
        logger.error(
            "{}{}{}".format(
                "The number of the sample inputs and outputs are different.\n",
                f"# of sample inputs: {len(in_sample_file_list)}\n",
                f"# of sample outputs: {len(out_sample_file_list)}\n",
            )
        )
        raise IrregularSampleFileError
    samples = []
    for in_sample_file, out_sample_file in zip(in_sample_file_list, out_sample_file_list):
        validate_sample_pair(in_sample_file, out_sample_file)
        samples.append((in_sample_file, out_sample_file))

    test_summary = run_for_samples(
        exec_file,
        samples,
        timeout_sec,
        judge_method,
        knock_out,
        skip_stderr_on_success,
        cwd=cwd,
        judge_program_language=judge_program_language,
    )

    if len(samples) == 0:
        print("No test cases")
        return False
    elif test_summary.success_count != len(samples):
        print(
            "{msg} (passed {success_count} of {total})".format(
                msg=with_color("Some cases FAILED", Fore.LIGHTRED_EX),
                success_count=test_summary.success_count,
                total=len(samples),
            )
        )
        return False
    elif test_summary.has_error_output:
        print(with_color("Passed all test case but with stderr. (Please remove stderr!)", Fore.LIGHTYELLOW_EX))
        return False
    else:
        print(with_color("Passed all test cases!!!", Fore.LIGHTGREEN_EX))
        return True


def get_metadata(metadata_file: str) -> Metadata:
    try:
        metadata = Metadata.load_from(metadata_file)
        return metadata
    except OSError:
        logger.warning(f"{metadata_file} is not found. Default metadata is selected. ")
        return DEFAULT_METADATA


USER_FACING_JUDGE_TYPE_LIST = ["normal", "absolute", "relative", "absolute_or_relative", "multisolution", "interactive"]


def str_to_bool(text: str) -> bool:
    """argparse `type` for boolean flags given as strings.

    `type=bool` must NOT be used in add_argument: bool("false") is True,
    which would silently invert the option's meaning."""
    if text.lower() in ("true", "1", "yes"):
        return True
    if text.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"boolean value must be one of true/false/1/0/yes/no, got '{text}'")


def _decide_judge_method(parsed_args: argparse.Namespace, metadata: Metadata, lang: Optional[Language]) -> Judge:
    def _decide_decimal_judge() -> DecimalJudge:
        if parsed_args.error_value is not None:
            diff = parsed_args.error_value
        elif isinstance(metadata.judge_method, DecimalJudge):
            diff = metadata.judge_method.diff
        else:
            diff = DEFAULT_EPS

        if parsed_args.judge_type:
            assert parsed_args.judge_type in ["absolute", "relative", "absolute_or_relative"]
            error_type = ErrorType(parsed_args.judge_type)
        elif isinstance(metadata.judge_method, DecimalJudge):
            error_type = metadata.judge_method.error_type
        else:
            raise Exception("Must not reach")

        return DecimalJudge(diff=diff, error_type=error_type)

    if parsed_args.judge_type is not None:
        if parsed_args.judge_type == "normal":
            return NormalJudge()
        elif parsed_args.judge_type in ["absolute", "relative", "absolute_or_relative"]:
            return _decide_decimal_judge()
        elif parsed_args.judge_type == "multisolution":
            assert lang is not None
            return MultiSolutionJudge()
        elif parsed_args.judge_type == "interactive":
            assert lang is not None
            return InteractiveJudge()
        else:
            logger.error(
                "Unknown judge type: {}. judge type must be one of [{}]".format(
                    parsed_args.judge_type, ", ".join(USER_FACING_JUDGE_TYPE_LIST)
                )
            )
            raise InvalidJudgeTypeError()

    if isinstance(metadata.judge_method, DecimalJudge):
        return _decide_decimal_judge()

    return metadata.judge_method


def main(prog: str, args: list[str]) -> bool:
    parser = argparse.ArgumentParser(prog=prog, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "--exec",
        "-e",
        help="File path to the execution target. [Default] Automatically detected exec file",
        default=None,
    )

    parser.add_argument(
        "--num",
        "-n",
        help="The case number to test (1-origin). All cases are tested if not specified.",
        type=int,
        default=None,
    )

    parser.add_argument("--dir", "-d", help="Target directory to test. [Default] Current directory", default=".")

    parser.add_argument("--timeout", "-t", help="Timeout for each test cases (sec) [Default] 1", type=int, default=1)

    parser.add_argument(
        "--knock-out",
        "-k",
        help="Stop execution immediately after any example's failure [Default] False",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--skip-almost-ac-feedback",
        "-s",
        help="Hide inputs and expected/actual outputs if result is correct and there are error outputs"
        " [Default] False,",
        action="store_true",
        default=False,
    )

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
        "--compile-before-testing",
        "-c",
        help="compile source before testing [true, false]:  [Default]: false",
        type=str_to_bool,
        default=None,
    )

    parser.add_argument(
        "--compile-only-when-diff-detected",
        help="compile only when diff detected [true, false] [Default]: true",
        type=str_to_bool,
        default=None,
    )

    parser.add_argument(
        "--config",
        help="File path to your config file\n{}{}".format(
            f"[Default (Primary)] {USER_CONFIG_PATH}\n",
            f"[Default (Secondary)] {get_default_config_path()}\n",
        ),
    )

    parsed_args = parser.parse_args(args)

    metadata_file = os.path.join(parsed_args.dir, "metadata.json")
    metadata = get_metadata(metadata_file)
    lang = metadata.lang
    assert lang is not None

    # TODO: Stop loading language-specific config because tester doesn't have and shouldn't have --lang params.
    # TODO: All information required to run tester should be from metadata.json except for etc config
    # TODO: https://github.com/kyuridenamida/atcoder-tools/issues/177
    config = get_config(parsed_args, lang)

    in_sample_file_list = sorted(glob.glob(os.path.join(parsed_args.dir, metadata.sample_in_pattern)))
    out_sample_file_list = sorted(glob.glob(os.path.join(parsed_args.dir, metadata.sample_out_pattern)))

    judge_method = _decide_judge_method(parsed_args, metadata, lang)

    if isinstance(judge_method, DecimalJudge):
        logger.info(f"Decimal number judge is enabled. type={judge_method.error_type.value}, diff={judge_method.diff}")

    if parsed_args.exec is not None:
        exec_file = parsed_args.exec
    elif config.etc_config.compile_before_testing:
        # Use atcoder-tools's functionality to compile source code
        try:
            compile_main_and_judge_programs(
                metadata, parsed_args.dir, force_compile=not config.etc_config.compile_only_when_diff_detected
            )
        except BadStatusCodeException as e:
            raise e
        exec_file = lang.get_test_command("main", parsed_args.dir)
    else:
        # TODO Have a smarter strategy to detect judge program
        excluded_exec_files = [os.path.join(parsed_args.dir, "judge"), os.path.join(parsed_args.dir, "judge.exe")]
        exec_file = infer_exec_file(glob.glob(os.path.join(parsed_args.dir, "*")), excluded_exec_files)
        logger.info(f"Inferred exec file: {exec_file}")

    if parsed_args.num is None:
        return run_all_tests(
            exec_file,
            in_sample_file_list,
            out_sample_file_list,
            parsed_args.timeout,
            parsed_args.knock_out,
            parsed_args.skip_almost_ac_feedback,
            judge_method,
            parsed_args.dir,
            lang,
        )  # TODO: pass judge_lang instead
    else:
        return run_single_test(
            exec_file,
            in_sample_file_list,
            out_sample_file_list,
            parsed_args.timeout,
            parsed_args.num,
            judge_method,
            parsed_args.dir,
            lang,
        )


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
