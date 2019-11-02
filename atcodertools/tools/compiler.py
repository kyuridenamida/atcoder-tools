#!/usr/bin/python3

import argparse
import os
import shutil
from atcodertools.common.judgetype import ErrorType, NormalJudge, DecimalJudge, MultiSolutionJudge, InteractiveJudge, JudgeType, NoJudgeTypeException, DEFAULT_EPS
from atcodertools.executils.run_command import run_command
from atcodertools.tools.models.metadata import Metadata
from atcodertools.common.language import Language, ALL_LANGUAGES, CPP, JAVA, RUST, PYTHON, NIM, DLANG, CSHARP
from atcodertools.tools.templates import get_default_judge_template_path


def compile(metadata):
    compile_cmd = metadata.lang.get_compile_command('main')
    print("Compileing: ")
    print(compile_cmd)
    print(run_command(compile_cmd, "./"))
    if metadata.judge_method.judge_type in [JudgeType.MultiSolution, JudgeType.Interactive]:
        print("Compile Judge...")
        compile_cmd = _compile_command(metadata.judge_method.judge_code_lang, metadata.judge_method.judge_code_filename)
        print(run_command(compile_cmd, "./"))
        print("MULTISOLUTION or INTERACTIVE")
    pass


def main(prog, args):
    print("compile!!")

    metadata = Metadata.load_from("./metadata.json")
    compile(metadata)

    
