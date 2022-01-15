from typing import List

from collections import OrderedDict

from atcodertools.fmtprediction.models.variable import SimpleVariable
from atcodertools.fmtprediction.models.variable_token import VariableToken
from atcodertools.fmtprediction.models.format import SingularPattern, Format, ParallelPattern, TwoDimensionalPattern, WrongGroupingError


class UnknownPeriodError(Exception):
    pass


class SimpleFormatPredictionFailedError(Exception):
    pass


def _predict_period(seq: List[int]):
    if len(seq) >= 2:
        span = seq[1] - seq[0]
        for cur, succ in zip(seq, seq[1:]):
            if succ - cur != span:
                raise UnknownPeriodError
        return span
    else:
        return 1


def _predict_simple_format_main(var_tokens: List[VariableToken], to_1d_flag) -> Format[SimpleVariable]:
    var_to_positions = {}
    var_to_simple_var = OrderedDict()

    # Pre-computation of the min / max value of each of the first and second
    # indices.
    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name

        if var_name not in var_to_simple_var:
            var_to_simple_var[var_name] = SimpleVariable.create(
                var_name, var_token.dim_num())
            var_to_positions[var_name] = []

        var_to_positions[var_name].append(pos)

        if var_token.dim_num() >= 2:
            var_to_simple_var[var_name].second_index.update(
                var_token.second_index)
        if var_token.dim_num() >= 1:
            var_to_simple_var[var_name].first_index.update(
                var_token.first_index)

    # Building format nodes
    already_processed_vars = set()

    root = Format()  # type: Format[SimpleVariable]
    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name
        simple_var = var_to_simple_var[var_name]

        if var_name in already_processed_vars:
            continue

        dim = var_token.dim_num()

        if pos in to_1d_flag:
            if dim == 2:
                # simple_var.first_index = simple_var.second_index
                simple_var.second_index = None
                dim = 1
            elif dim == 1:
                simple_var.first_index = None
                dim = 0

        if dim == 0:
            root.push_back(SingularPattern(simple_var))
            already_processed_vars.add(var_name)
        elif dim == 1:
            period = _predict_period(var_to_positions[var_name])
            parallel_vars_group = [var_to_simple_var[token.var_name]
                                   for token in var_tokens[pos:pos + period]]
            try:
                root.push_back(ParallelPattern(parallel_vars_group))
            except WrongGroupingError:
                raise
            for var in parallel_vars_group:
                already_processed_vars.add(var.name)
        elif dim == 2:
            root.push_back(TwoDimensionalPattern(simple_var))
        else:
            raise NotImplementedError
        already_processed_vars.add(var_name)
    return root


def _predict_1d_flag_pos(var_tokens: List[VariableToken]) -> List[Format[SimpleVariable]]:
    var_to_positions = {}
    var_to_simple_var = OrderedDict()

    # Pre-computation of the min / max value of each of the first and second
    # indices.
    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name

        if var_name not in var_to_simple_var:
            var_to_simple_var[var_name] = SimpleVariable.create(
                var_name, var_token.dim_num())
            var_to_positions[var_name] = []

        var_to_positions[var_name].append(pos)

        if var_token.dim_num() >= 2:
            var_to_simple_var[var_name].second_index.update(
                var_token.second_index)
        if var_token.dim_num() >= 1:
            var_to_simple_var[var_name].first_index.update(
                var_token.first_index)

    # Building format nodes
    already_processed_vars = set()

    result = []
    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name
        # simple_var = var_to_simple_var[var_name]

        if var_name in already_processed_vars:
            continue

        dim = var_token.dim_num()

        if dim == 0:
            pass
        elif dim == 1:
            try:
                period = _predict_period(var_to_positions[var_name])
            except UnknownPeriodError:
                continue
            if period == 1:
                result.append(pos)
            parallel_vars_group = [var_to_simple_var[token.var_name]
                                   for token in var_tokens[pos:pos + period]]
            # try:
            #     root.push_back(ParallelPattern(parallel_vars_group))
            # except WrongGroupingError:
            #     raise
            for var in parallel_vars_group:
                already_processed_vars.add(var.name)
        elif dim == 2:
            result.append(pos)
        else:
            raise NotImplementedError
        already_processed_vars.add(var_name)
    return result


def predict_simple_format(var_tokens: List[VariableToken]) -> Format[SimpleVariable]:
    flag_pos = _predict_1d_flag_pos(var_tokens)
    result = []
    for b in range(1 << len(flag_pos)):
        to_1d_flag = set()
        for i in range(len(flag_pos)):
            if b & (1 << i):
                to_1d_flag.add(flag_pos[i])
        try:
            result.append(_predict_simple_format_main(var_tokens, to_1d_flag))
        except (WrongGroupingError, UnknownPeriodError):
            continue
            # raise SimpleFormatPredictionFailedError
    return result
