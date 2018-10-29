import copy
from typing import List, Dict, Optional

from core.Calculator import CalcNode, CalcParseError
from core.models.VariableToken import VariableToken, TokenizedFormat
from core.utils import divide_consecutive_vars, normalize_index, is_ascii, is_noise


class PreTokenizer:
    @staticmethod
    def tokenize(input_format: str) -> List[str]:
        input_format = input_format.replace("\n", " ").replace("…", " ").replace("...", " ").replace(
            "..", " ").replace("\ ", " ").replace("}", "} ").replace("　", " ")
        input_format = divide_consecutive_vars(input_format)
        input_format = normalize_index(input_format)
        input_format = input_format.replace("{", "").replace("}", "")
        tokens = [x for x in input_format.split() if x != "" and is_ascii(x) and not is_noise(x)]
        return tokens


class TokenManager:
    tokens = []
    pos = 0

    def __init__(self, tokens):
        self.tokens = tokens

    def peek(self):
        return self.tokens[self.pos]

    def is_terminal(self):
        return self.pos == len(self.tokens)

    def go_next(self):
        self.pos += 1

    def go_back(self):
        self.pos -= 1


class FormatSearcher:
    answers = None
    token_manager = None
    max_variables_count = None

    def __init__(self, tokens):
        self.token_manager = TokenManager(tokens)

    def search(self, max_variables_count) -> List[TokenizedFormat]:
        self.max_variables_count = max_variables_count
        self.answers = []
        self.inner_search([], {})
        return self.answers

    def inner_search(self, var_token_seq, var_to_dim_num: Dict[str, int]):
        if len(var_to_dim_num) > self.max_variables_count:
            return

        if self.token_manager.is_terminal():
            self.answers.append(TokenizedFormat(copy.deepcopy(var_token_seq)))
            return

        for var_token in self.possible_var_tokens(self.token_manager.peek(), var_to_dim_num):
            next_var_to_dim_num = copy.deepcopy(var_to_dim_num)
            next_var_to_dim_num[var_token.var_name] = var_token.dim_num()
            try:
                var_token_seq.append(var_token)
                self.token_manager.go_next()
                self.inner_search(var_token_seq, next_var_to_dim_num)
            finally:
                self.token_manager.go_back()
                var_token_seq.pop()

    @staticmethod
    def possible_var_tokens(token: str, current_var_to_dim_num: Dict[str, int]) -> List[VariableToken]:
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
                    for sub_var in CalcNode(index).get_all_varnames():
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
        self.tokens = PreTokenizer().tokenize(input_format)

    def compute_formats_with_minimal_vars(self) -> List[TokenizedFormat]:
        """
        Quite fast for realistic instances.
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
