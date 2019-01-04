import os
from typing import List

from atcodertools.codegen.code_generator import CodeGenerator
from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from atcodertools.models.sample import Sample
from atcodertools.models.predictor.format_prediction_result import FormatPredictionResult


def _make_text_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)


def create_code_from(result: FormatPredictionResult,
                     constants: ProblemConstantSet,
                     code_generator: CodeGenerator,
                     file_path: str):
    _make_text_file(file_path, code_generator.generate_code(result, constants))


def create_example(example: Sample, in_example_name: str, out_example_name: str):
    _make_text_file(in_example_name, example.get_input())
    _make_text_file(out_example_name, example.get_output())


def create_examples(examples: List[Sample],
                    target_dir_path: str,
                    in_example_name_format: str = "in_{}.txt",
                    out_example_name_format: str = "out_{}.txt"):
    def gen_path(file):
        return os.path.join(target_dir_path, file)

    for index, example in enumerate(examples):
        create_example(example,
                       gen_path(in_example_name_format.format(index + 1)),
                       gen_path(out_example_name_format.format(index + 1)))
