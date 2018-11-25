from core.FormatAnalyzer import format_analyse
from core.FormatTokenizer import get_all_format_probabilities
from core.utils import is_ascii, is_noise
from core.utils import divide_consecutive_vars, normalize_index


class FormatPredictResult:
    def __init__(self, analyzed_root=None, var_information=None):
        self.analyzed_root = analyzed_root
        self.var_information = var_information


def format_predictor(format, samples):
    format = format.replace("\n", " ").replace("…", " ").replace("...", " ").replace(
        "..", " ").replace("\ ", " ").replace("}", "} ").replace("　", " ")
    format = divide_consecutive_vars(format)
    format = normalize_index(format)
    format = format.replace("{", "").replace("}", "")

    tokens = [x for x in format.split(
        " ") if x != "" and is_ascii(x) and not is_noise(x)]
    tokenize_result = get_all_format_probabilities(tokens)

    for to_1d_flag in [False, True]:
        for candidate_format in tokenize_result:
            rootnode, varinfo = format_analyse(
                candidate_format, to_1d_flag)
            try:
                current_dic = {}
                for sample in samples:
                    sample = sample[0].replace(" ", "[SP] ")
                    sample = sample.replace("\n", "[NL] ")
                    # print(samples)
                    # tokens = [(name,sep)]*
                    tokens = [(x[:-4], '     ' if x[-4:] == '[SP]' else '\n' if x[-4:] == '[NL]' else 'ERR') for x in
                              sample.split(" ") if x != ""]  # "abc[SP]" -> "abc
                    # print(tokens)
                    current_dic = rootnode.verify_and_get_types(
                        tokens, current_dic)

                for k, var in current_dic.items():
                    varinfo[k].type = var[1]
                res = FormatPredictResult(rootnode, varinfo)
                # print(str(rootnode))
                return res
            except Exception as e:
                pass

    return None
