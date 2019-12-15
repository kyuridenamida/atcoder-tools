import re
from typing import List, Dict, Any

from atcodertools.fmtprediction.models.calculator import EvaluateError
from atcodertools.fmtprediction.models.type import Type
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.variable import SimpleVariable
from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.format import Format, SingularPattern, TwoDimensionalPattern, \
    ParallelPattern
from atcodertools.fmtprediction.token_manager import TokenManager


class TypesUnmatchedError(Exception):
    pass


class ParseError(Exception):
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


def is_float(text):
    return re.match(r"-?\d+\.\d+$", text) is not None


def is_int(text):
    if text == "0":
        return True
    if re.match(r"-?\d+$", text) is None:
        return False
    if text[0] == "0":
        return False
    if len(text) > 19 or (text[0] == '-' and len(text) > 20):
        return False
    return True


def _convert_to_proper_type(value: str) -> Any:
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    return value


class TypePredictor:

    def __init__(self, fmt: Format[SimpleVariable]):
        self._fmt = fmt
        self._fetch_generator_instance = self._fetch_generator()
        self._var_to_type = {}  # type: Dict[str, Type]
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

    def _refresh(self, var: SimpleVariable, value: Any):
        type_ = Type.from_py_type(type(value))

        if var.name in self._var_to_type:
            self._var_to_type[var.name] = self._var_to_type[
                var.name].intersect(type_)
        else:
            self._var_to_type[var.name] = type_
            self._var_to_actual_value[var.name] = value

    def _fetch(self) -> SimpleVariable:
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


def merge_type_dicts(to_dict: Dict[str, Type], src_dict: Dict[str, Type]):
    for k, v in src_dict.items():
        if k in to_dict:
            to_dict[k] = to_dict[k].intersect(v)
        else:
            to_dict[k] = v
    return to_dict


def predict_types(simple_format: Format[SimpleVariable], samples: List[Sample]) -> Dict[str, Type]:
    res_type_dict = {}
    for sample in samples:
        token_manager = TokenManager(sample.get_input().split())
        predictor = TypePredictor(simple_format)
        try:
            while not token_manager.is_terminal():
                predictor.feed(token_manager.next())
            predictor.ensure_terminal()
            res_type_dict = merge_type_dicts(
                res_type_dict,
                predictor.get_typing_result())
        except (
                TooLessFetchesError, TooManyFetchesError, KeyError, InvalidLoopSizeError,
                InvalidLoopIndexError, EvaluateError):
            raise TypePredictionFailedError

    return res_type_dict
