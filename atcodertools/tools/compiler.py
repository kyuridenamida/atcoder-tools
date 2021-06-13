#!/usr/bin/python3
import argparse

from atcodertools.executils.run_command import run_command_with_returncode
from atcodertools.tools.models.metadata import Metadata
from atcodertools.common.language import Language
import os
import pathlib


class BadStatusCodeException(Exception):
    pass


def _compile(code_filename: str, exec_filename: str, compile_command: str, cwd: str, force_compile: bool) -> None:
    if not force_compile:
        code_path = pathlib.Path(os.path.join(cwd, code_filename))
        exec_path_name = os.path.join(cwd, exec_filename)

        if os.path.exists(exec_path_name) and code_path.stat().st_mtime < pathlib.Path(exec_path_name).stat().st_mtime:
            print("No need to compile")
            return

    print("Compiling... (command: `{}`)".format(compile_command))
    code, stdout = run_command_with_returncode(compile_command, cwd)
    print(stdout)
    if code != 0:
        raise BadStatusCodeException


def compile_main_and_judge_programs(lang: Language, cwd="./", force_compile=False, compile_command=None) -> None:
    print("[Main Program]")
    if compile_command is None:
        compile_command = lang.get_compile_command('main')
    code_filename = lang.get_code_filename('main')
    exec_filename = lang.get_exec_filename('main')

    try:
        _compile(code_filename, exec_filename,
                 compile_command, cwd, force_compile)
    except BadStatusCodeException as e:
        raise e


def main(prog, args):
    parser = argparse.ArgumentParser(
        prog=prog,
        usage="Compile your program in the current directory (no argument)",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--compile-command',
                        help='set compile command'
                             ' [Default]: None',
                        type=str,
                        default=None)

    parser.add_argument('--compile-only-when-diff-detected',
                        help='compile only when diff detected [true, false]'
                             ' [Default]: true',
                        type=bool,
                        default=False)

    args = parser.parse_args(args)

    metadata = Metadata.load_from("./metadata.json")
    force_compile = not args.compile_only_when_diff_detected
    compile_main_and_judge_programs(metadata.lang, force_compile=force_compile,
                                    compile_command=args.compile_command)
