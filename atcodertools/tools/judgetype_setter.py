#!/usr/bin/python3

import argparse
import os
from atcodertools.common.judgetype import ErrorType, NormalJudge, DecimalJudge, MultiSolutionJudge, InteractiveJudge, JudgeType, NoJudgeTypeException, DEFAULT_EPS
from atcodertools.tools.models.metadata import Metadata


def main(prog, args):
    if len(args) == 0:
        print("Usage: ")
        return
    new_judge_type = args[0]

    metadata = Metadata.load_from("./metadata.json")
    old_judge_type = metadata.judge_method.judge_type.value

    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--error-value', '-v',
                        help='error value for decimal number judge:'
                             ' [Default] ' + str(DEFAULT_EPS),
                        type=float,
                        default=None)

    parser.add_argument('--error-type', '-t',
                        help='error type'
                             ' must be one of [{}]'.format(
                                 ', '.join([x.value for x in list(ErrorType)])),
                        type=str,
                        default=None)

    args = parser.parse_args(args[1:])

    if new_judge_type != old_judge_type:
        if new_judge_type == JudgeType.Normal.value:
            metadata.judge_method = NormalJudge()
        elif new_judge_type == JudgeType.Decimal.value:
            metadata.judge_method = DecimalJudge()
        elif new_judge_type == JudgeType.MultiSolution.value:
            metadata.judge_method = MultiSolutionJudge()
        elif new_judge_type == JudgeType.Interactive.value:
            metadata.judge_method = InteractiveJudge()
        else:
            raise NoJudgeTypeException()

    if new_judge_type == JudgeType.Decimal.value:
        if args.error_value is not None:
            metadata.judge_method.diff = args.error_value
        if args.error_type is not None:
            metadata.judge_method.error_type = args.error_type
    elif new_judge_type == JudgeType.MultiSolution.value:
        if not os.path.exists("./judge.cpp"):
            print("touch ./judge.cpp (multi sotlution)")
        else:
            print("Judge Code exists")
    elif new_judge_type == JudgeType.Interactive.value:
        if not os.path.exists("./judge.cpp"):
            print("touch ./judge.cpp (interactive)")
        else:
            print("Judge Code exists")

    metadata.save_to("./metadata.json")
