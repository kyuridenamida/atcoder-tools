#!/usr/bin/python3

from atcodertools.common.judgetype import JudgeType
from atcodertools.executils.run_command import run_command_with_returncode
from atcodertools.tools.models.metadata import Metadata
import os
import pathlib


def compile(code_filename, exec_filename, compile_cmd, cwd):
    code_p = pathlib.Path(cwd + '/' + code_filename)
    if os.path.exists(cwd + '/' + exec_filename):
        exec_p = pathlib.Path(cwd + '/' + exec_filename)
    else:
        exec_p = None
    if exec_p is not None and code_p.stat().st_mtime < exec_p.stat().st_mtime:
        print("No need to compile")
        return True
    else:
        print("Compileing: ")
        print(compile_cmd)
        code, stdout = run_command_with_returncode(compile_cmd, cwd)
        print(stdout)
        if code == 0:
            return True
        else:
            return False


def compile_codes(metadata, cwd="./"):
    valid = True
    lang = metadata.lang
    print("code file: ")
    compile_cmd = lang.get_compile_command('main')
    code_filename = lang.get_code_filename('main')
    exec_filename = lang.get_exec_filename('main')
    code = compile(code_filename, exec_filename, compile_cmd, cwd)
    if not code:
        valid = False
    if metadata.judge_method.judge_type in [JudgeType.MultiSolution, JudgeType.Interactive]:
        print("judge file: ")
        lang = metadata.judge_method.judge_code_lang
        compile_cmd = lang.get_compile_command('judge')
        code_filename = lang.get_code_filename('judge')
        exec_filename = lang.get_exec_filename('judge')

        code = compile(code_filename, exec_filename, compile_cmd, cwd)
        if not code:
            valid = False
    return valid


def main(prog, args):
    metadata = Metadata.load_from("./metadata.json")
    compile_codes(metadata)
