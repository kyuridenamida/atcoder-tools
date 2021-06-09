#!/usr/bin/python3
import argparse
import glob
import os
import platform
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from os.path import expanduser

from colorama import Fore

from atcodertools.common.judgetype import ErrorType, NormalJudge, DecimalJudge, Judge

from atcodertools.common.language import Language
from atcodertools.common.logging import logger
from atcodertools.executils.run_program import ExecResult, ExecStatus, run_program
from atcodertools.tools.models.metadata import Metadata, DEFAULT_METADATA
from atcodertools.tools.utils import with_color
from atcodertools.tools.compiler import compile_main_and_judge_programs, BadStatusCodeException
from atcodertools.config.config import Config
from atcodertools.tools import get_default_config_path

DEFAULT_EPS = 0.000000001


USER_CONFIG_PATH = os.path.join(expanduser("~"), ".atcodertools.toml")


class NoExecutableFileError(Exception):
    pass


class IrregularSampleFileError(Exception):
    pass


class InvalidJudgeTypeError(Exception):
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


def infer_exec_file(filenames: List[str], excluded_exec_files: List[str]):
    exec_files = [name for name in sorted(
        filenames) if is_executable_file(name) and (name not in excluded_exec_files)]

    if len(exec_files) == 0:
        raise NoExecutableFileError
    else:
        exec_file = exec_files[0]
    if len(exec_files) >= 2:
        logger.warning("{0}  {1}".format(
            "There're multiple executable files. '{exec_file}' is selected.".format(
                exec_file=exec_file),
            "The candidates were {exec_files}.".format(exec_files=exec_files)))
    return exec_file


def infer_case_num(sample_filename: str):
    sample_basename = os.path.basename(sample_filename)
    result = ""
    for c in sample_basename:
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
                    skip_io_on_success: bool = False, cwd="./") -> TestSummary:
    success_count = 0
    has_error_output = False
    for in_sample_file, out_sample_file in sample_pair_list:
        # Run program
        exec_res = run_program(exec_file, in_sample_file,
                               timeout_sec=timeout_sec,
                               current_working_dir=cwd)

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
                    judge_method: Judge, cwd: str, judge_program_language: Language) -> bool:
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
        exec_file, [(in_sample_file, out_sample_file)], timeout_sec, judge_method, cwd=cwd)

    return test_summary.success_count == 1 and not test_summary.has_error_output


def run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, timeout_sec: int, knock_out: bool,
                  skip_stderr_on_success: bool, judge_method: Judge, cwd: str,
                  judge_program_language: Language) -> bool:
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
        exec_file, samples, timeout_sec, judge_method, knock_out, skip_stderr_on_success, cwd=cwd)

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


def get_metadata(metadata_file: str) -> Metadata:
    try:
        metadata = Metadata.load_from(metadata_file)
        return metadata
    except IOError:
        logger.warning("{} is not found. Default metadata is selected. ".format(
            metadata_file)
        )
        return DEFAULT_METADATA


USER_FACING_JUDGE_TYPE_LIST = [
    "normal", "absolute", "relative", "absolute_or_relative"]


def _decide_judge_method(args: argparse.Namespace, metadata: Metadata, lang: Optional[Language]):
    def _decide_decimal_judge():
        if args.error_value is not None:
            diff = args.error_value
        elif isinstance(metadata.judge_method, DecimalJudge):
            diff = metadata.judge_method.diff
        else:
            diff = DEFAULT_EPS

        if args.judge_type:
            assert args.judge_type in ["absolute",
                                       "relative", "absolute_or_relative"]
            error_type = ErrorType(args.judge_type)
        elif isinstance(metadata.judge_method, DecimalJudge):
            error_type = metadata.judge_method.error_type
        else:
            raise Exception("Must not reach")

        return DecimalJudge(diff=diff, error_type=error_type)

    if args.judge_type is not None:
        if args.judge_type == "normal":
            return NormalJudge()
        elif args.judge_type in ["absolute", "relative", "absolute_or_relative"]:
            return _decide_decimal_judge()
        else:
            logger.error("Unknown judge type: {}. judge type must be one of [{}]".format(
                args.judge_type, ", ".join(USER_FACING_JUDGE_TYPE_LIST)))
            raise InvalidJudgeTypeError()

    if isinstance(metadata.judge_method, DecimalJudge):
        return _decide_decimal_judge()

    return metadata.judge_method


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

    parser.add_argument('--compile-before-testing',
                        help='compile source before testing: '
                             ' [Default]: disable',
                        action='store_true')

    parser.add_argument('--compile-only-when-diff-detected',
                        help='compile only when diff detected'
                             ' [Default]: disable',
                        action='store_true')

    parser.add_argument('--compile-command',
                        help='set compile command'
                             ' [Default]: None',
                        type=str,
                        default=None)

    parser.add_argument("--config",
                        help="File path to your config file\n{0}{1}".format("[Default (Primary)] {}\n".format(
                            USER_CONFIG_PATH),
                            "[Default (Secondary)] {}\n".format(
                                get_default_config_path())),
                        default=None)

    args = parser.parse_args(args)
    if args.config is None:
        if os.path.exists(USER_CONFIG_PATH):
            args.config = USER_CONFIG_PATH
        else:
            args.config = get_default_config_path()

    metadata_file = os.path.join(args.dir, "metadata.json")
    metadata = get_metadata(metadata_file)
    lang = metadata.lang

    # TODO: Stop loading language-specific config because tester doesn't have and shouldn't have --lang params.
    # TODO: All information required to run tester should be from metadata.json except for etc config
    # TODO: https://github.com/kyuridenamida/atcoder-tools/issues/177

    with open(args.config, "r") as f:
        config = Config.load(f)
    if args.compile_before_testing:
        config.etc_config.compile_before_testing = True
    if args.compile_only_when_diff_detected:
        config.etc_config.compile_only_when_diff_detected = True

    in_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, metadata.sample_in_pattern)))
    out_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, metadata.sample_out_pattern)))

    judge_method = _decide_judge_method(args, metadata, lang)

    if isinstance(judge_method, DecimalJudge):
        logger.info("Decimal number judge is enabled. type={}, diff={}".format(
            judge_method.error_type.value, judge_method.diff))

    if args.exec is not None:
        exec_file = args.exec
    elif config.etc_config.compile_before_testing:
        # Use atcoder-tools's functionality to compile source code
        force_compile = not config.etc_config.compile_only_when_diff_detected
        try:
            compile_main_and_judge_programs(
                metadata.lang,
                args.dir,
                force_compile=force_compile,
                compile_command=args.compile_command
            )
        except BadStatusCodeException as e:
            raise e
        exec_file = lang.get_test_command('main', args.dir)
    else:
        # TODO Have a smarter strategy to detect judge program
        excluded_exec_files = [
            os.path.join(args.dir, "judge"),
            os.path.join(args.dir, "judge.exe")
        ]
        exec_file = infer_exec_file(
            glob.glob(os.path.join(args.dir, '*')), excluded_exec_files)
        logger.info("Inferred exec file: {}".format(exec_file))

    if args.num is None:
        return run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.knock_out,
                             args.skip_almost_ac_feedback, judge_method, args.dir,
                             lang)  # TODO: pass judge_lang instead
    else:
        return run_single_test(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.num,
                               judge_method, args.dir, lang)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
