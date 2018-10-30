from typing import List

from core.AtCoderClient import ProblemContent
from core.FormatAnalyzer import format_analyse
from core.FormatTokenizer import FormatTokenizer
from core.TypePredictor import type_predictor


class FormatPredictResult:
    def __init__(self, analyzed_root=None, var_information=None):
        self.analyzed_root = analyzed_root
        self.var_information = var_information


class FormatPredictor:
    @staticmethod
    def predict(content: ProblemContent):
        input_format = content.get_input_format()
        samples = content.get_samples()
        var_tokens = FormatTokenizer(input_format).compute_formats_with_minimal_vars()

        for to_1d_flag in [False, True]:
            for candidate_format in var_tokens:
                try:
                    fmt = format_analyse(candidate_format.var_tokens, to_1d_flag)
                    print(fmt, samples)
                    print(type_predictor(fmt, samples))
                except Exception as e:
                    print("err")
                    pass
                #
                # try:
                #     current_dic = {}
                #     for sample in samples:
                #         sample = sample.get_input().replace(" ", "[SP] ")
                #         sample = sample.replace("\n", "[NL] ")
                #         tokens = [(x[:-4], '     ' if x[-4:] == '[SP]' else '\n' if x[-4:] == '[NL]' else 'ERR') for x
                #                   in
                #                   sample.split(" ") if x != ""]  # "abc[SP]" -> "abc
                #         current_dic = root_node.verify_and_get_types(
                #             tokens, current_dic)
                #
                #     for k, var in current_dic.items():
                #         var_info[k].type = var[1]
                #     res = FormatPredictResult(root_node, var_info)
                #     return res
                # except Exception:
                #     pass

        return None
