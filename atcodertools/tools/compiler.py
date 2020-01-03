#!/usr/bin/python3
import argparse

from atcodertools.common.judgetype import JudgeType
from atcodertools.executils.run_command import run_command_with_returncode
from atcodertools.tools.models.metadata import Metadata
import os
import pathlib


class BadStatusCodeException(Exception):
    pass


def _compile(code_filename: str, exec_filename: str, compile_cmd: str, cwd: str, force_compile: bool) -> None:
    if not force_compile:
        code_path = pathlib.Path(os.path.join(cwd, code_filename))
        exec_path_name = os.path.join(cwd, exec_filename)

        if os.path.exists(exec_path_name) and code_path.stat().st_mtime < pathlib.Path(exec_path_name).stat().st_mtime:
            print("No need to compile")
            return

    print("Compiling... (command: `{}`)".format(compile_cmd))
    code, stdout = run_command_with_returncode(compile_cmd, cwd)
    print(stdout)
    if code != 0:
        raise BadStatusCodeException


def compile_main_and_judge_programs(metadata: Metadata, cwd="./", force_compile=False) -> None:
    lang = metadata.lang
    print("[Main Program]")
    compile_cmd = lang.get_compile_command('main')
    code_filename = lang.get_code_filename('main')
    exec_filename = lang.get_exec_filename('main')

    try:
        _compile(code_filename, exec_filename, compile_cmd, cwd, force_compile)
    except BadStatusCodeException as e:
        raise e

    if metadata.judge_method.judge_type in [JudgeType.MultiSolution, JudgeType.Interactive]:
        print("[Judge Program]")
        lang = metadata.judge_method.judge_code_lang
        compile_cmd = lang.get_compile_command('judge')
        code_filename = lang.get_code_filename('judge')
        exec_filename = lang.get_exec_filename('judge')

        try:
            _compile(code_filename, exec_filename,
                     compile_cmd, cwd, force_compile)
        except BadStatusCodeException as e:
            raise e


def main(prog, args):
    parser = argparse.ArgumentParser(
        prog=prog,
        usage="Compile your program in the current directory (no argument)",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.parse_args(args)

    metadata = Metadata.load_from("./metadata.json")
    compile_main_and_judge_programs(metadata, force_compile=True)
