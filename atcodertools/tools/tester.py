#!/usr/bin/python3
import argparse
import glob
import os
import platform
import re
import sys
from pathlib import Path
from typing import List, Tuple

from colorama import Fore

from atcodertools.common.judgetype import ErrorType, NormalJudge, DecimalJudge, Judge, JudgeType
from atcodertools.common.logging import logger
from atcodertools.executils.run_program import ExecResult, ExecStatus, run_program
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.utils import with_color

DEFAULT_EPS = 0.000000001


class NoExecutableFileError(Exception):
    pass


class IrregularSampleFileError(Exception):
    pass


class TestSummary:
    def __init__(self, success_count: int, has_error_output: bool):
        self.success_count = success_count
        self.has_error_output = has_error_output

    def __eq__(self, other):
        return self.success_count == other.success_count and self.has_error_output == other.has_error_output


def is_executable_file(file_name):
    if platform.system() == "Windows":
        return any(
            re.match(r"^.*\{ext}$".format(ext=ext), file_name, re.IGNORECASE)
            for ext in os.environ.get("pathext", default="").split(";"))
    else:
        return os.access(file_name, os.X_OK) and Path(file_name).is_file() \
            and file_name.find(".cpp") == -1 and not file_name.endswith(".txt")  # cppやtxtを省くのは一応の Cygwin 対策


def infer_exec_file(filenames):
    exec_files = [name for name in sorted(
        filenames) if is_executable_file(name)]

    if len(exec_files) == 0:
        raise NoExecutableFileError

    exec_file = exec_files[0]
    if len(exec_files) >= 2:
        logger.warning("{0}  {1}".format(
            "There're multiple executable files. '{exec_file}' is selected.".format(
                exec_file=exec_file),
            "The candidates were {exec_files}.".format(exec_files=exec_files)))
    return exec_file


def infer_case_num(sample_filename: str):
    result = ""
    for c in sample_filename:
        if c.isdigit():
            result += c
    return int(result)


def build_details_str(exec_res: ExecResult, input_file: str, output_file: str) -> str:
    res = ""

    def append(text: str, end='\n'):
        nonlocal res
        res += text + end

    with open(output_file, "r") as f:
        expected_output = f.read()

    append(with_color("[Input]", Fore.LIGHTMAGENTA_EX))
    with open(input_file, "r") as f:
        append(f.read(), end='')

    append(with_color("[Expected]", Fore.LIGHTMAGENTA_EX))
    append(expected_output, end='')

    append(with_color("[Received]", Fore.LIGHTMAGENTA_EX))
    append(exec_res.output, end='')

    if exec_res.status != ExecStatus.NORMAL:
        append(with_color("Aborted ({})\n".format(
            exec_res.status.name), Fore.LIGHTYELLOW_EX))

    if exec_res.has_stderr():
        append(with_color("[Error]", Fore.LIGHTYELLOW_EX))
        append(exec_res.stderr, end='')
    return res


def run_for_samples(exec_file: str, sample_pair_list: List[Tuple[str, str]], timeout_sec: int,
                    judge_method: Judge = NormalJudge(), knock_out: bool = False,
                    skip_io_on_success: bool = False) -> TestSummary:
    success_count = 0
    has_error_output = False
    for in_sample_file, out_sample_file in sample_pair_list:
        # Run program
        exec_res = run_program(exec_file, in_sample_file,
                               timeout_sec=timeout_sec)

        # Output header
        with open(out_sample_file, 'r') as f:
            answer_text = f.read()

        is_correct = exec_res.is_correct_output(answer_text, judge_method)
        has_error_output = has_error_output or exec_res.has_stderr()

        if is_correct:
            if exec_res.has_stderr():
                message = with_color(
                    "CORRECT but with stderr (Please remove stderr!)", Fore.LIGHTYELLOW_EX)
            else:
                message = "{} {elapsed} ms".format(
                    with_color("PASSED", Fore.LIGHTGREEN_EX),
                    elapsed=exec_res.elapsed_ms)
            success_count += 1
        else:
            if exec_res.status == ExecStatus.NORMAL:
                message = with_color("WA", Fore.LIGHTRED_EX)
            else:
                message = with_color(
                    exec_res.status.name, Fore.LIGHTYELLOW_EX)

        print("# {case_name} ... {message}".format(
            case_name=os.path.basename(in_sample_file),
            message=message,
        ))

        # Output details for incorrect results or has stderr.
        if not is_correct or (exec_res.has_stderr() and not skip_io_on_success):
            print('{}\n'.format(build_details_str(
                exec_res, in_sample_file, out_sample_file)))

        if knock_out and not is_correct:
            print('Stop testing ...')
            break
    return TestSummary(success_count, has_error_output)


def validate_sample_pair(in_sample_file, out_sample_file):
    if infer_case_num(in_sample_file) != infer_case_num(out_sample_file):
        logger.error(
            'The file combination of {} and {} is wrong.'.format(
                in_sample_file,
                out_sample_file
            ))
        raise IrregularSampleFileError


def run_single_test(exec_file, in_sample_file_list, out_sample_file_list, timeout_sec: int, case_num: int,
                    judge_method: Judge) -> bool:
    def single_or_none(lst: List):
        if len(lst) == 1:
            return lst[0]
        if len(lst) == 0:
            return None
        raise IrregularSampleFileError(
            "Multiple samples are detected for given case num: {}".format(lst))

    in_sample_file = single_or_none(
        [name for name in in_sample_file_list if infer_case_num(name) == case_num])
    out_sample_file = single_or_none(
        [name for name in out_sample_file_list if infer_case_num(name) == case_num])

    if in_sample_file is None or out_sample_file is None:
        print("Invalid test case number: {}".format(case_num))
        return False

    validate_sample_pair(in_sample_file, out_sample_file)

    test_summary = run_for_samples(
        exec_file, [(in_sample_file, out_sample_file)], timeout_sec, judge_method)

    return test_summary.success_count == 1 and not test_summary.has_error_output


def run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, timeout_sec: int, knock_out: bool,
                  skip_stderr_on_success: bool, judge_method) -> bool:
    if len(in_sample_file_list) != len(out_sample_file_list):
        logger.error("{0}{1}{2}".format(
            "The number of the sample inputs and outputs are different.\n",
            "# of sample inputs: {}\n".format(len(in_sample_file_list)),
            "# of sample outputs: {}\n".format(len(out_sample_file_list))))
        raise IrregularSampleFileError
    samples = []
    for in_sample_file, out_sample_file in zip(in_sample_file_list, out_sample_file_list):
        validate_sample_pair(in_sample_file, out_sample_file)
        samples.append((in_sample_file, out_sample_file))

    test_summary = run_for_samples(
        exec_file, samples, timeout_sec, judge_method, knock_out, skip_stderr_on_success)

    if len(samples) == 0:
        print("No test cases")
        return False
    elif test_summary.success_count != len(samples):
        print("{msg} (passed {success_count} of {total})".format(
            msg=with_color("Some cases FAILED", Fore.LIGHTRED_EX),
            success_count=test_summary.success_count,
            total=len(samples),
        ))
        return False
    elif test_summary.has_error_output:
        print(with_color(
            "Passed all test case but with stderr. (Please remove stderr!)", Fore.LIGHTYELLOW_EX))
        return False
    else:
        print(with_color("Passed all test cases!!!", Fore.LIGHTGREEN_EX))
        return True


DEFAULT_IN_EXAMPLE_PATTERN = 'in_*.txt'
DEFAULT_OUT_EXAMPLE_PATTERN = "out_*.txt"


def get_sample_patterns_and_judge_method(metadata_file: str) -> Tuple[str, str, Judge]:
    try:
        metadata = Metadata.load_from(metadata_file)
        return metadata.sample_in_pattern, metadata.sample_out_pattern, metadata.judge_method
    except IOError:
        logger.warning("{} is not found. Assume the example file name patterns are {} and {}".format(
            metadata_file,
            DEFAULT_IN_EXAMPLE_PATTERN,
            DEFAULT_OUT_EXAMPLE_PATTERN)
        )
        return DEFAULT_IN_EXAMPLE_PATTERN, DEFAULT_OUT_EXAMPLE_PATTERN, NormalJudge()


USER_FACING_JUDGE_TYPE_LIST = [
    "normal", "absolute", "relative", "absolute_or_relative"]


def main(prog, args) -> bool:
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--exec", '-e',
                        help="File path to the execution target. [Default] Automatically detected exec file",
                        default=None)

    parser.add_argument("--num", '-n',
                        help="The case number to test (1-origin). All cases are tested if not specified.",
                        type=int,
                        default=None)

    parser.add_argument("--dir", '-d',
                        help="Target directory to test. [Default] Current directory",
                        default=".")

    parser.add_argument("--timeout", '-t',
                        help="Timeout for each test cases (sec) [Default] 1",
                        type=int,
                        default=1)

    parser.add_argument("--knock-out", '-k',
                        help="Stop execution immediately after any example's failure [Default] False",
                        action="store_true",
                        default=False)

    parser.add_argument('--skip-almost-ac-feedback', '-s',
                        help='Hide inputs and expected/actual outputs if result is correct and there are error outputs'
                             ' [Default] False,',
                        action='store_true',
                        default=False)

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

    args = parser.parse_args(args)
    exec_file = args.exec or infer_exec_file(
        glob.glob(os.path.join(args.dir, '*')))

    metadata_file = os.path.join(args.dir, "metadata.json")
    in_ex_pattern, out_ex_pattern, judge_method = get_sample_patterns_and_judge_method(
        metadata_file)

    in_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, in_ex_pattern)))
    out_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, out_ex_pattern)))

    user_input_decimal_error_type = None
    if args.judge_type is not None:
        if args.judge_type == "normal":
            judge_method = NormalJudge()
        elif args.judge_type in ["absolute", "relative", "absolute_or_relative"]:
            user_input_decimal_error_type = ErrorType(args.judge_type)
        else:
            logger.error("Unknown judge type: {}. judge type must be one of [{}]".format(
                args.judge_type, ", ".join(USER_FACING_JUDGE_TYPE_LIST)))
            sys.exit(-1)

    user_input_error_value = args.error_value

    if isinstance(judge_method, DecimalJudge):
        judge_method = DecimalJudge(error_type=user_input_decimal_error_type or judge_method.error_type,
                                    diff=user_input_error_value or judge_method.diff)
    elif user_input_decimal_error_type is not None:
        judge_method = DecimalJudge(error_type=user_input_decimal_error_type,
                                    diff=user_input_error_value or DEFAULT_EPS)
    elif user_input_error_value is not None:
        assert judge_method.judge_type == JudgeType.Normal
        logger.warn("error_value {} is ignored because this is normal judge".format(
            user_input_error_value))

    if isinstance(judge_method, DecimalJudge):
        logger.info("Decimal number judge is enabled. type={}, diff={}".format(
            judge_method.error_type.value, judge_method.diff))

    if args.num is None:
        return run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.knock_out,
                             args.skip_almost_ac_feedback, judge_method)
    else:
        return run_single_test(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.num,
                               judge_method)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
