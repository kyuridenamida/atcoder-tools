from typing import Optional, List


class VariableToken:
    var_name = None
    first_index = None
    second_index = None

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

    def is_valid(self):
        if not self.has_valid_var_name():
            return False
        if not self.is_valid_index(self.first_index):
            return False
        if not self.is_valid_index(self.second_index):
            return False
        return True

    def has_valid_var_name(self):
        return all(c.isalpha() or c == '_' for c in self.var_name)

    @staticmethod
    def is_valid_index(index):
        if index is None:
            return True

        if not index[-1].isalpha() and not index[-1].isdigit():
            return False
        if index.find(',') != -1:
            return False
        return True

    def dim_num(self):
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0


class TokenizedFormat:
    var_tokens = None

    def __init__(self, var_tokens: List[VariableToken]):
        self.var_tokens = var_tokens

