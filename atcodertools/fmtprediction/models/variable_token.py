import re
from typing import Optional

VALID_VAR_NAME_REG_EXP = re.compile("[a-zA-Z_]+")


class VariableToken:
    """
    This model is used on the tokenization stage to store variable information with all string indices
    This class supports up to 2 dimensions.
    """

    def __init__(self, var_name: str, first_index: Optional[str], second_index: Optional[str]) -> None:
        def normalize(x: Optional[str]) -> Optional[str]:
            if x is None:
                return None
            return x.rstrip(",")

        def fixed_var_name(x: str) -> str:
            if x[-1] == "_":
                return x[:-1]
            return x

        normalized_var_name = normalize(var_name)
        assert normalized_var_name is not None
        self.var_name = fixed_var_name(normalized_var_name)
        self.first_index = normalize(first_index)
        self.second_index = normalize(second_index)

    def dim_num(self) -> int:
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0

    def is_valid(self) -> bool:
        if not self._has_valid_var_name():
            return False
        if not self._is_valid_index(self.first_index):
            return False
        return self._is_valid_index(self.second_index)

    def _has_valid_var_name(self) -> bool:
        return VALID_VAR_NAME_REG_EXP.fullmatch(self.var_name) is not None

    @staticmethod
    def _is_valid_index(index: Optional[str]) -> bool:
        if index is None:
            return True
        if len(index) == 0:
            return False
        if not index[-1].isalpha() and not index[-1].isdigit():
            return False
        return index.find(",") == -1


class TokenizedFormat:
    def __init__(self, var_tokens: list[VariableToken]) -> None:
        self.var_tokens = var_tokens
