import copy
from typing import List, Dict

from core.Calculator import CalcNode, CalcParseError
from core.models.tokenizer.VariableToken import VariableToken, TokenizedFormat


# Utils
from core.utils.TokenManager import TokenManager


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def is_noise(s):
    return s == ":" or s == "...." or s == "..." or s == ".." or s == "."


def normalize_index(text):
    return text.replace("{(", "").replace(")}", "")


def divide_consecutive_vars(text):
    res_text = ""
    i = 0
    while i < len(text):
        if text[i] == "_":
            res_text += "_"
            i += 1

            if i < len(text) and text[i].isdigit():
                while i < len(text) and text[i].isdigit():
                    res_text += text[i]
                    i += 1
            elif i < len(text) and text[i].isalpha():
                res_text += text[i]
                i += 1
            if i < len(text) and text[i].isalpha():
                res_text += " "
        else:
            res_text += text[i]
            i += 1
    return res_text


def sanitized_tokens(input_format: str) -> List[str]:
    input_format = input_format.replace("\n", " ").replace("…", " ").replace("...", " ").replace(
        "..", " ").replace("\ ", " ").replace("}", "} ").replace("　", " ")
    input_format = divide_consecutive_vars(input_format)
    input_format = normalize_index(input_format)
    input_format = input_format.replace("{", "").replace("}", "")
    tokens = [x for x in input_format.split() if x != "" and is_ascii(x) and not is_noise(x)]
    return tokens


class FormatSearcher:
    _answers = None
    _token_manager = None
    _max_variables_count = None

    def __init__(self, tokens):
        self._token_manager = TokenManager(tokens)

    def search(self, max_variables_count) -> List[TokenizedFormat]:
        self._max_variables_count = max_variables_count
        self._answers = []
        self._inner_search([], {})
        return self._answers

    def _inner_search(self, var_token_seq, var_to_dim_num: Dict[str, int]):
        if len(var_to_dim_num) > self._max_variables_count:
            return

        if self._token_manager.is_terminal():
            self._answers.append(TokenizedFormat(copy.deepcopy(var_token_seq)))
            return

        for var_token in self._possible_var_tokens(self._token_manager.peek(), var_to_dim_num):
            next_var_to_dim_num = copy.deepcopy(var_to_dim_num)
            next_var_to_dim_num[var_token.var_name] = var_token.dim_num()
            try:
                var_token_seq.append(var_token)
                self._token_manager.go_next()
                self._inner_search(var_token_seq, next_var_to_dim_num)
            finally:
                self._token_manager.go_back()
                var_token_seq.pop()

    @staticmethod
    def _possible_var_tokens(token: str, current_var_to_dim_num: Dict[str, int]) -> List[VariableToken]:
        """
        Only considers to divide the given token into at most 3 pieces (that is, to assume at most 2 dimensional indexes).
        :param token: e.g. "N", "abc_1_2" or "a_1 ... a_N"
        :param current_var_to_dim_num: utilized to detect unknown variables (for pruning purpose)
        """
        var_token_candidates = [VariableToken(token, None, None)]
        var_token_candidates += [VariableToken(token[:i], token[i:], None) for i in range(1, len(token))]
        for i in range(1, len(token)):
            for j in range(i + 1, len(token)):
                var_token_candidates += [VariableToken(token[:i], token[i:j], token[j:])]

        def check_if_possible(var_token: VariableToken):
            # check syntax error
            if not var_token.is_valid():
                return False

            # check kind of synonym error using current_var_to_dim_num
            for index in [var_token.first_index, var_token.second_index]:
                if index is None:
                    continue

                try:
                    for sub_var in CalcNode(index).get_all_variables():
                        if sub_var not in current_var_to_dim_num:
                            return False
                except CalcParseError:
                    return False

            if var_token.var_name in current_var_to_dim_num \
                    and current_var_to_dim_num[var_token.var_name] != var_token.dim_num():
                return False
            return True

        return [var_token for var_token in var_token_candidates if check_if_possible(var_token)]


class FormatTokenizer:
    def __init__(self, input_format: str):
        self.tokens = sanitized_tokens(input_format)

    def compute_formats_with_minimal_vars(self) -> List[TokenizedFormat]:
        """
        Fast enough for realistic instances.
        This method stores possible formats with the smallest number of variables to self.possible_formats
        """

        searcher = FormatSearcher(self.tokens)
        for max_variable_length in range(1, 20):
            result = searcher.search(max_variable_length)
            if result:
                return result
        raise NoFormatFoundError


class NoFormatFoundError(Exception):
    pass
