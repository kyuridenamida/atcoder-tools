import re
from typing import List, Optional


VALID_VAR_NAME_REG_EXP = re.compile(
    "[a-zA-Z_]+"
)


class VariableToken:
    """
    Variable information used during format tokenization.

    Up to three indices are supported.
    """

    def __init__(
        self,
        var_name: str,
        first_index: Optional[str],
        second_index: Optional[str],
        third_index: Optional[str] = None,
    ):
        def normalize(value):
            if value is None:
                return None
            return value.rstrip(",")

        def fixed_var_name(value):
            if value.endswith("_"):
                return value[:-1]
            return value

        self.var_name = fixed_var_name(
            normalize(var_name)
        )
        self.first_index = normalize(first_index)
        self.second_index = normalize(second_index)
        self.third_index = normalize(third_index)

    def dim_num(self):
        if self.third_index:
            return 3
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0

    def is_valid(self):
        if not self._has_valid_var_name():
            return False

        for index in (
            self.first_index,
            self.second_index,
            self.third_index,
        ):
            if not self._is_valid_index(index):
                return False

        return True

    def _has_valid_var_name(self):
        return (
            VALID_VAR_NAME_REG_EXP.fullmatch(
                self.var_name
            )
            is not None
        )

    @staticmethod
    def _is_valid_index(index):
        if index is None:
            return True
        if len(index) == 0:
            return False
        if (
            not index[-1].isalpha()
            and not index[-1].isdigit()
        ):
            return False
        if index.find(",") != -1:
            return False
        return True


class TokenizedFormat:
    def __init__(
        self,
        var_tokens: List[VariableToken],
    ):
        self.var_tokens = var_tokens
