#!/usr/bin/python3

from atcodertools.common.judgetype import JudgeType
from atcodertools.executils.run_command import run_command
from atcodertools.tools.models.metadata import Metadata


def compile(metadata):
    compile_cmd = metadata.lang.get_compile_command('main')
    print("Compileing: ")
    print(compile_cmd)
    print(run_command(compile_cmd, "./"))
    if metadata.judge_method.judge_type in [JudgeType.MultiSolution, JudgeType.Interactive]:
        print("Compile Judge...")
        compile_cmd = metadata.judge_method.judge_code_lang.get_compile_command(
            metadata.judge_method.judge_code_filename)
        print(run_command(compile_cmd, "./"))
    pass


def main(prog, args):
    metadata = Metadata.load_from("./metadata.json")
    compile(metadata)
