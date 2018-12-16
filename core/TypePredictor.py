import copy
import re
from typing import List, Dict, Union

from core.models.Sample import Sample
from core.models.analyzer.AnalyzedVariable import AnalyzedVariable
from core.models.analyzer.Index import Index
from core.models.analyzer.SimpleFormat import SimpleFormat, SingularPattern, TwoDimensionalPattern, ParallelPattern
from core.utils.TokenManager import TokenManager


class TypesUnmatchedError(Exception):
    pass


class ParseError(Exception):
    pass


class UpCastingError(Exception):
    pass


class UnknownSpanError(Exception):
    pass


def up_cast(old_type, new_type):
    if old_type == new_type:
        return old_type
    if (old_type == int and new_type == float) or (old_type == float or new_type == int):
        return float
    raise UpCastingError


def is_float(text):
    return re.match("-?\d+\.\d+$", text) is not None


def is_int(text):
    return re.match("-?\d+$", text) is not None


def convert_to_proper_type(value: str):
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    return value


class TooManyFetchesError(Exception):
    pass


class TooLessFetchesError(Exception):
    pass


class TypePredictor:
    def __init__(self, fmt: SimpleFormat):
        self._fmt = fmt
        self._fetch_generator_instance = self._fetch_generator()
        self._var_to_type = {}
        self._var_to_actual_value = {}  # If there are multiple values, only the first value is recorded.

    def get_typing_result(self):
        return self._var_to_type

    def ensure_terminal(self):
        if next(self._fetch_generator_instance) is None:
            return
        raise TooLessFetchesError

    def feed(self, sample_token: str):
        var = self._fetch()
        self._refresh(var, convert_to_proper_type(sample_token))

    def _loop_size(self, loop_index: Index):
        min_value = loop_index.min_index.evaluate(self._var_to_actual_value)
        max_value = loop_index.max_index.evaluate(self._var_to_actual_value)
        return max_value - min_value + 1

    def _refresh(self, var: AnalyzedVariable, value: any):
        if var.var_name in self._var_to_type:
            self._var_to_type[var.var_name] = up_cast(self._var_to_type[var.var_name], type(value))
        else:
            self._var_to_type[var.var_name] = type(value)
            self._var_to_actual_value[var.var_name] = value

    def _fetch(self) -> AnalyzedVariable:
        res = next(self._fetch_generator_instance)
        if res is None:
            raise TooManyFetchesError
        return res

    def _fetch_generator(self):
        for pattern in self._fmt.sequence:
            if type(pattern) == SingularPattern:
                yield pattern.var
            elif type(pattern) == TwoDimensionalPattern:
                for _ in range(self._loop_size(pattern.var.first_index)):
                    for _ in range(self._loop_size(pattern.var.second_index)):
                        yield pattern.var
            elif type(pattern) == ParallelPattern:
                for _ in range(self._loop_size(pattern.loop_index)):
                    for v in pattern.vars:
                        yield v
        yield None
        raise TooManyFetchesError()


def merge_type_dicts(to_dict, src_dict):
    for k, v in src_dict.items():
        if k in to_dict:
            to_dict[k] = up_cast(to_dict[k], v)
        else:
            to_dict[k] = v
    return to_dict


def type_predictor(fmt: SimpleFormat, samples: List[Sample]) -> Dict[str, type]:
    res_type_dict = {}
    for sample in samples:
        token_manager = TokenManager(sample.get_input().split())
        predictor = TypePredictor(fmt)
        while not token_manager.is_terminal():
            predictor.feed(token_manager.next())
        predictor.ensure_terminal()
        res_type_dict = merge_type_dicts(res_type_dict, predictor.get_typing_result())
    return res_type_dict
