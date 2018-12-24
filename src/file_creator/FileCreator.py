import os
from typing import List

from code_generation import CodeGenerator
from models.Sample import Sample
from models.predictor.FormatPredictionResult import FormatPredictionResult


def create_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)


class FileCreator:
    @staticmethod
    def create_code_from_prediction_result(result: FormatPredictionResult, code_generator: CodeGenerator, file_path: str):
        create_file(file_path, code_generator.generate_code(result))

    @staticmethod
    def create_example(example: Sample, in_example_name: str, out_example_name: str):
        create_file(in_example_name, example.get_input())
        create_file(out_example_name, example.get_output())

    @staticmethod
    def create_examples(examples: List[Sample],
                        target_dir_path: str,
                        in_example_name_format: str = "in_{}.txt",
                        out_example_name_format: str = "out_{}.txt"):
        def gen_path(file):
            return os.path.join(target_dir_path, file)

        for index, example in enumerate(examples):
            FileCreator.create_example(example,
                                gen_path(in_example_name_format.format(index + 1)),
                                gen_path(out_example_name_format.format(index + 1)))