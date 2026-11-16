import re
from collections.abc import Iterator
from typing import Any, Optional, Union

from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.models.calculator import EvaluateError
from atcodertools.fmtprediction.models.format import Format, ParallelPattern, SingularPattern, TwoDimensionalPattern
from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import SimpleVariable
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


def is_float(text: str) -> bool:
    return re.match(r"-?\d+\.\d+$", text) is not None


def is_int(text: str) -> bool:
    if text == "0":
        return True
    if re.match(r"-?\d+$", text) is None:
        return False
    if text[0] == "0":
        return False
    return not (len(text) > 19 or (text[0] == "-" and len(text) > 20))


def _convert_to_proper_type(value: str) -> Union[int, float, str]:
    if is_int(value):
        return int(value)
    elif is_float(value):
        return float(value)
    return value


class TypePredictor:
    def __init__(self, fmt: Format[SimpleVariable]) -> None:
        self._fmt = fmt
        self._fetch_generator_instance = self._fetch_generator()
        self._var_to_type: dict[str, Type] = {}
        # If there are multiple values, only the first value is recorded.
        self._var_to_actual_value: dict[str, Any] = {}

    def get_typing_result(self) -> dict[str, Type]:
        return self._var_to_type

    def ensure_terminal(self) -> None:
        if next(self._fetch_generator_instance) is None:
            return
        raise TooLessFetchesError

    def feed(self, sample_token: str) -> None:
        var = self._fetch()
        self._refresh(var, _convert_to_proper_type(sample_token))

    def _loop_size(self, loop_index: Index) -> int:
        if loop_index.min_index is None or loop_index.max_index is None:
            raise InvalidLoopIndexError

        min_value: int = loop_index.min_index.evaluate(self._var_to_actual_value)
        max_value: int = loop_index.max_index.evaluate(self._var_to_actual_value)

        try:
            return max_value - min_value + 1
        except Exception as e:
            raise InvalidLoopSizeError from e

    def _refresh(self, var: SimpleVariable, value: Any) -> None:
        type_ = Type.from_py_type(type(value))

        if var.name in self._var_to_type:
            self._var_to_type[var.name] = self._var_to_type[var.name].intersect(type_)
        else:
            self._var_to_type[var.name] = type_
            self._var_to_actual_value[var.name] = value

    def _fetch(self) -> SimpleVariable:
        res = next(self._fetch_generator_instance)
        if res is None:
            raise TooManyFetchesError
        return res

    def _fetch_generator(self) -> Iterator[Optional[SimpleVariable]]:
        for pattern in self._fmt.sequence:
            if isinstance(pattern, SingularPattern):
                yield pattern.var
            elif isinstance(pattern, TwoDimensionalPattern):
                for _ in range(self._loop_size(pattern.var.first_index)):
                    for _ in range(self._loop_size(pattern.var.second_index)):
                        yield pattern.var
            elif isinstance(pattern, ParallelPattern):
                for _ in range(self._loop_size(pattern.loop_index)):
                    yield from pattern.vars
        yield None
        raise TooManyFetchesError()


def merge_type_dicts(to_dict: dict[str, Type], src_dict: dict[str, Type]) -> dict[str, Type]:
    for k, v in src_dict.items():
        if k in to_dict:
            to_dict[k] = to_dict[k].intersect(v)
        else:
            to_dict[k] = v
    return to_dict


def predict_types(simple_format: Format[SimpleVariable], samples: list[Sample]) -> dict[str, Type]:
    res_type_dict: dict[str, Type] = {}
    for sample in samples:
        token_manager = TokenManager(sample.get_input().split())
        predictor = TypePredictor(simple_format)
        try:
            while not token_manager.is_terminal():
                predictor.feed(token_manager.next())
            predictor.ensure_terminal()
            res_type_dict = merge_type_dicts(res_type_dict, predictor.get_typing_result())
        except (
            TooLessFetchesError,
            TooManyFetchesError,
            KeyError,
            InvalidLoopSizeError,
            InvalidLoopIndexError,
            EvaluateError,
        ) as e:
            raise TypePredictionFailedError from e

    return res_type_dict
