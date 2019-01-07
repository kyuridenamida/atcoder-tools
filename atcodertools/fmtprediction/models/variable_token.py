import re
from typing import Optional, List


VALID_VAR_NAME_REG_EXP = re.compile("[a-zA-Z_]+")


class VariableToken:

    """
    This model is used on the tokenization stage to store variable information with all string indices
    This class supports up to 2 dimensions.
    """

    def __init__(self, var_name: str, first_index: Optional[str], second_index: Optional[str]):
        def normalize(x: str):
            if x is None:
                return None
            return x.rstrip(",")

        def fixed_var_name(x: str):
            if x[-1] == "_":
                return x[:-1]
            return x

        self.var_name = fixed_var_name(normalize(var_name))
        self.first_index = normalize(first_index)
        self.second_index = normalize(second_index)

    def dim_num(self):
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0

    def is_valid(self):
        if not self._has_valid_var_name():
            return False
        if not self._is_valid_index(self.first_index):
            return False
        if not self._is_valid_index(self.second_index):
            return False
        return True

    def _has_valid_var_name(self):
        return VALID_VAR_NAME_REG_EXP.fullmatch(self.var_name) is not None

    @staticmethod
    def _is_valid_index(index):
        if index is None:
            return True
        if len(index) == 0:
            return False
        if not index[-1].isalpha() and not index[-1].isdigit():
            return False
        if index.find(',') != -1:
            return False
        return True


class TokenizedFormat:

    def __init__(self, var_tokens: List[VariableToken]):
        self.var_tokens = var_tokens
