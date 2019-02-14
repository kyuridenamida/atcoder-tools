#!/usr/bin/python3
import argparse
import glob
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

from colorama import Fore

from atcodertools.executils.run_program import ExecResult, ExecStatus, run_program
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.utils import with_color


class NoExecutableFileError(Exception):
    pass


class IrregularSampleFileError(Exception):
    pass


def is_executable_file(file_name):
    return os.access(file_name, os.X_OK) and Path(file_name).is_file() \
        and file_name.find(".cpp") == -1 and not file_name.endswith(".txt")  # cppやtxtを省くのは一応の Cygwin 対策


def infer_exec_file(filenames):
    exec_files = [name for name in sorted(
        filenames) if is_executable_file(name)]

    if len(exec_files) == 0:
        raise NoExecutableFileError

    exec_file = exec_files[0]
    if len(exec_files) >= 2:
        logging.warning("{0}  {1}".format(
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

    append(with_color("[Input]", Fore.LIGHTMAGENTA_EX))
    with open(input_file, "r") as f:
        append(f.read(), end='')

    append(with_color("[Expected]", Fore.LIGHTMAGENTA_EX))
    with open(output_file, "r") as f:
        append(f.read(), end='')

    append(with_color("[Received]", Fore.LIGHTMAGENTA_EX))
    append(exec_res.output, end='')
    if exec_res.status != ExecStatus.NORMAL:
        append(with_color("Aborted ({})\n".format(
            exec_res.status.name), Fore.LIGHTYELLOW_EX))

    if exec_res.has_stderr():
        append(with_color("[Error]", Fore.LIGHTYELLOW_EX))
        append(exec_res.stderr, end='')
    return res


def run_for_samples(exec_file: str, sample_pair_list: List[Tuple[str, str]], timeout_sec: int, knock_out: bool = False):
    success_count = 0
    for in_sample_file, out_sample_file in sample_pair_list:
        # Run program
        exec_res = run_program(exec_file, in_sample_file,
                               timeout_sec=timeout_sec)

        # Output header
        with open(out_sample_file, 'r') as f:
            answer_text = f.read()

        is_correct = exec_res.is_correct_output(answer_text)
        passed = is_correct and not exec_res.has_stderr()

        if passed:
            message = "{} {elapsed} ms".format(
                with_color("PASSED", Fore.LIGHTGREEN_EX),
                elapsed=exec_res.elapsed_ms)
            success_count += 1
        else:
            if is_correct:
                message = with_color(
                    "CORRECT but with stderr (Please remove stderr!)", Fore.LIGHTYELLOW_EX)
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

        # Output details for incorrect results.
        if not passed:
            print('{}\n'.format(build_details_str(
                exec_res, in_sample_file, out_sample_file)))
            if knock_out:
                print('Stop testing ...')
                break
    return success_count


def validate_sample_pair(in_sample_file, out_sample_file):
    if infer_case_num(in_sample_file) != infer_case_num(out_sample_file):
        logging.error(
            'The file combination of {} and {} is wrong.'.format(
                in_sample_file,
                out_sample_file
            ))
        raise IrregularSampleFileError


def run_single_test(exec_file, in_sample_file_list, out_sample_file_list, timeout_sec: int, case_num: int) -> bool:
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

    success_count = run_for_samples(
        exec_file, [(in_sample_file, out_sample_file)], timeout_sec)

    return success_count == 1


def run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, timeout_sec: int, knock_out: bool) -> bool:
    if len(in_sample_file_list) != len(out_sample_file_list):
        logging.error("{0}{1}{2}".format(
            "The number of the sample inputs and outputs are different.\n",
            "# of sample inputs: {}\n".format(len(in_sample_file_list)),
            "# of sample outputs: {}\n".format(len(out_sample_file_list))))
        raise IrregularSampleFileError
    samples = []
    for in_sample_file, out_sample_file in zip(in_sample_file_list, out_sample_file_list):
        validate_sample_pair(in_sample_file, out_sample_file)
        samples.append((in_sample_file, out_sample_file))

    success_count = run_for_samples(exec_file, samples, timeout_sec, knock_out)

    if len(samples) == 0:
        print("No test cases")
        return False
    elif success_count != len(samples):
        print("{msg} (passed {success_count} of {total})".format(
            msg=with_color("Some cases FAILED", Fore.LIGHTRED_EX),
            success_count=success_count,
            total=len(samples),
        ))
        return False
    else:
        print(with_color("Passed all test cases!!!", Fore.LIGHTGREEN_EX))
        return True


DEFAULT_IN_EXAMPLE_PATTERN = 'in_*.txt'
DEFAULT_OUT_EXAMPLE_PATTERN = "out_*.txt"


def get_sample_patterns(metadata_file: str) -> Tuple[str, str]:
    try:
        metadata = Metadata.load_from(metadata_file)
        return metadata.sample_in_pattern, metadata.sample_out_pattern
    except IOError:
        logging.warning("{} is not found. Assume the example file name patterns are {} and {}".format(
            metadata_file,
            DEFAULT_IN_EXAMPLE_PATTERN,
            DEFAULT_OUT_EXAMPLE_PATTERN)
        )
        return DEFAULT_IN_EXAMPLE_PATTERN, DEFAULT_OUT_EXAMPLE_PATTERN


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

    args = parser.parse_args(args)
    exec_file = args.exec or infer_exec_file(
        glob.glob(os.path.join(args.dir, '*')))

    metadata_file = os.path.join(args.dir, "metadata.json")
    in_ex_pattern, out_ex_pattern = get_sample_patterns(metadata_file)

    in_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, in_ex_pattern)))
    out_sample_file_list = sorted(
        glob.glob(os.path.join(args.dir, out_ex_pattern)))

    if args.num is None:
        return run_all_tests(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.knock_out)
    else:
        return run_single_test(exec_file, in_sample_file_list, out_sample_file_list, args.timeout, args.num)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
