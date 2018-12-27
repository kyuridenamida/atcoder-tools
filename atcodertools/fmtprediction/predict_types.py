import re
from typing import List, Dict

from atcodertools.models.sample import Sample
from atcodertools.models.analyzer.analyzed_variable import AnalyzedVariable
from atcodertools.models.analyzer.index import Index
from atcodertools.models.analyzer.simple_format import SimpleFormat, SingularPattern, TwoDimensionalPattern, \
    ParallelPattern
from atcodertools.fmtprediction.token_manager import TokenManager


class TypesUnmatchedError(Exception):
    pass


class ParseError(Exception):
    pass


class UpCastingError(Exception):
    pass


class UnknownSpanError(Exception):
    pass


class TooManyFetchesError(Exception):
    pass


class TooLessFetchesError(Exception):
    pass


class TypePredictionFailedError(Exception):
    pass


class InvalidLoopSizeError(Exception):
    pass


class InvalidLoopIndexError(Exception):
    pass


UP_CAST_TABLE = {int: {}, str: {}, float: {}}

UP_CAST_TABLE[int][int] = int
UP_CAST_TABLE[int][str] = str
UP_CAST_TABLE[int][float] = float

UP_CAST_TABLE[str] = {}
UP_CAST_TABLE[str][int] = str
UP_CAST_TABLE[str][str] = str
UP_CAST_TABLE[str][float] = str

UP_CAST_TABLE[float] = {}
UP_CAST_TABLE[float][int] = float
UP_CAST_TABLE[float][str] = str
UP_CAST_TABLE[float][float] = float


def up_cast(old_type, new_type):
    try:
        return UP_CAST_TABLE[old_type][new_type]
    except KeyError:
        raise UpCastingError


def is_float(text):
    return re.match(r"-?\d+\.\d+$", text) is not None


def is_int(text):
    return re.match(r"-?\d+$", text) is not None


def _convert_to_proper_type(value: str):
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    return value


class TypePredictor:

    def __init__(self, fmt: SimpleFormat):
        self._fmt = fmt
        self._fetch_generator_instance = self._fetch_generator()
        self._var_to_type = {}
        # If there are multiple values, only the first value is recorded.
        self._var_to_actual_value = {}

    def get_typing_result(self):
        return self._var_to_type

    def ensure_terminal(self):
        if next(self._fetch_generator_instance) is None:
            return
        raise TooLessFetchesError

    def feed(self, sample_token: str):
        var = self._fetch()
        self._refresh(var, _convert_to_proper_type(sample_token))

    def _loop_size(self, loop_index: Index):
        if loop_index.min_index is None or loop_index.max_index is None:
            raise InvalidLoopIndexError

        min_value = loop_index.min_index.evaluate(self._var_to_actual_value)
        max_value = loop_index.max_index.evaluate(self._var_to_actual_value)

        try:
            return max_value - min_value + 1
        except Exception:
            raise InvalidLoopSizeError

    def _refresh(self, var: AnalyzedVariable, value: any):
        if var.var_name in self._var_to_type:
            self._var_to_type[var.var_name] = up_cast(
                self._var_to_type[var.var_name],
                type(value))
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
            if isinstance(pattern, SingularPattern):
                yield pattern.var
            elif isinstance(pattern, TwoDimensionalPattern):
                for _ in range(self._loop_size(pattern.var.first_index)):
                    for _ in range(self._loop_size(pattern.var.second_index)):
                        yield pattern.var
            elif isinstance(pattern, ParallelPattern):
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
        try:
            while not token_manager.is_terminal():
                predictor.feed(token_manager.next())
            predictor.ensure_terminal()
            res_type_dict = merge_type_dicts(
                res_type_dict,
                predictor.get_typing_result())
        except (
                TooLessFetchesError, TooManyFetchesError, KeyError, InvalidLoopSizeError, UpCastingError,
                InvalidLoopIndexError):
            raise TypePredictionFailedError

    return res_type_dict
