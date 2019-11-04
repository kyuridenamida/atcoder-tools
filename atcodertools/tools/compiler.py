#!/usr/bin/python3

from atcodertools.common.judgetype import JudgeType
from atcodertools.executils.run_command import run_command
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
    else:
        print("Compileing: ")
        print(compile_cmd)
        print(run_command(compile_cmd, cwd))


def compile_codes(metadata, cwd="./"):
    lang = metadata.lang
    print("code file: ")
    compile_cmd = lang.get_compile_command('main')
    code_filename = lang.get_code_filename('main')
    exec_filename = lang.get_exec_filename('main')
    compile(code_filename, exec_filename, compile_cmd, cwd)
    if metadata.judge_method.judge_type in [JudgeType.MultiSolution, JudgeType.Interactive]:
        print("judge file: ")
        lang = metadata.judge_method.judge_code_lang
        compile_cmd = lang.get_compile_command('judge')
        code_filename = lang.get_code_filename('judge')
        exec_filename = lang.get_exec_filename('judge')

        compile(code_filename, exec_filename, compile_cmd, cwd)
        print(run_command(compile_cmd, cwd))
    pass


def main(prog, args):
    metadata = Metadata.load_from("./metadata.json")
    compile_codes(metadata)
