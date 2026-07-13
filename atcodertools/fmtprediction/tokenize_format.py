import copy
from itertools import combinations
from typing import List, Dict

from atcodertools.fmtprediction.models.calculator import (
    CalcNode,
    CalcParseError,
)
from atcodertools.fmtprediction.models.variable_token import (
    VariableToken,
    TokenizedFormat,
)

from atcodertools.fmtprediction.token_manager import TokenManager


def _is_ascii(s):
    return all(ord(c) < 128 for c in s)


DOTS_PATTERNS = ["ldots", "cdots", "vdots", "ddots", "dots"]


def _is_noise(s):
    if any(pattern in s for pattern in DOTS_PATTERNS):
        return True

    return s == ":" or s == "...." or s == "..." or s == ".." or s == "."


def _normalize_index(text):
    return text.replace("{(", "").replace(")}", "")


def _divide_consecutive_vars(text):
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


def _remove_spaces_in_curly_brackets(input_format):
    res = []
    nest = 0
    for c in input_format:
        if c == '{':
            nest += 1
        elif c == '}':
            nest -= 1

        if c == ' ' and nest > 0:
            continue

        res.append(c)

    return "".join(res)


def _sanitized_tokens(input_format: str) -> List[str]:
    input_format = (
        input_format.replace("\n", " ")
        .replace("…", " ")
        .replace("...", " ")
        .replace("..", " ")
        .replace("\\ ", " ")
        .replace("}", "} ")
        .replace("　", " ")
        .replace(", ", ",")
    )
    input_format = _remove_spaces_in_curly_brackets(input_format)
    input_format = _divide_consecutive_vars(input_format)
    input_format = _normalize_index(input_format)
    input_format = input_format.replace("{", "").replace("}", "")

    tokens = [
        x for x in input_format.split(
        ) if x != "" and _is_ascii(
            x) and not _is_noise(
            x)]
    return tokens


class FormatSearcher:

    def __init__(self, tokens):
        self._token_manager = TokenManager(tokens)
        self._answers = None
        self._max_variables_count = None

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

        for var_token in self._possible_var_tokens(
            self._token_manager.peek(),
            var_to_dim_num,
        ):
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
    def _possible_var_tokens(
        token: str,
        current_var_to_dim_num: Dict[str, int],
    ) -> List[VariableToken]:
        """
        Divide a token into a variable name and up to
        three index expressions.

        Examples include ``N``, ``a_1``,
        ``a_1,2`` and ``a_1,2,3``.
        """
        candidates = [
            VariableToken(
                token,
                None,
                None,
                None,
            )
        ]

        for first_split in range(
            1,
            len(token),
        ):
            candidates.append(
                VariableToken(
                    token[:first_split],
                    token[first_split:],
                    None,
                    None,
                )
            )

        for first_split in range(
            1,
            len(token),
        ):
            for second_split in range(
                first_split + 1,
                len(token),
            ):
                candidates.append(
                    VariableToken(
                        token[:first_split],
                        token[
                            first_split:second_split
                        ],
                        token[second_split:],
                        None,
                    )
                )

        three_dimensional_splits = sorted(
            {
                boundary
                for position, character in enumerate(
                    token
                )
                if character in ("_", ",")
                for boundary in (
                    position,
                    position + 1,
                )
                if 0 < boundary < len(token)
            }
        )

        for (
            first_split,
            second_split,
            third_split,
        ) in combinations(
            three_dimensional_splits,
            3,
        ):
            candidates.append(
                VariableToken(
                    token[:first_split],
                    token[
                        first_split:second_split
                    ],
                    token[
                        second_split:third_split
                    ],
                    token[third_split:],
                )
            )

        def check_if_possible(var_token):
            if not var_token.is_valid():
                return False

            for index in (
                var_token.first_index,
                var_token.second_index,
                var_token.third_index,
            ):
                if index is None:
                    continue

                try:
                    variables = (
                        CalcNode.parse(index)
                        .get_all_variables()
                    )
                except CalcParseError:
                    return False

                for sub_var in variables:
                    if (
                        sub_var
                        not in current_var_to_dim_num
                    ):
                        return False

            if (
                var_token.var_name
                in current_var_to_dim_num
                and current_var_to_dim_num[
                    var_token.var_name
                ]
                != var_token.dim_num()
            ):
                return False

            return True

        return [
            candidate
            for candidate in candidates
            if check_if_possible(candidate)
        ]


def search_formats_with_minimum_vars(
    input_format: str,
) -> List[TokenizedFormat]:
    """
    Fast enough for realistic instances.
    This method returns possible formats with the smallest number of variables.
    """
    tokens = _sanitized_tokens(input_format)
    searcher = FormatSearcher(tokens)
    for max_variable_length in range(1, 20):
        result = searcher.search(max_variable_length)
        if result:
            return result
    raise NoFormatFoundError


class NoFormatFoundError(Exception):
    pass
