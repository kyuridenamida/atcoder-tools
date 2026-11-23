from typing import Dict, List

from collections import OrderedDict

from atcodertools.fmtprediction.models.variable import SimpleVariable
from atcodertools.fmtprediction.models.variable_token import VariableToken
from atcodertools.fmtprediction.models.format import (
    Format,
    ParallelPattern,
    SingularPattern,
    ThreeDimensionalPattern,
    TwoDimensionalPattern,
    WrongGroupingError,
)


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


def _vote_inner_dimensions(
    var_tokens: List[VariableToken],
) -> Dict[str, List[int]]:
    """
    For each multidimensional variable, count how often each index
    position changes between adjacent occurrences in the token stream.

    Within a compact character row such as ``s_{i,1} s_{i,2} ...`` the
    column index varies while the row index stays fixed, so the most
    frequently varying index is the inner dimension that the 1-D
    collapse should drop.  For the transposed ``c_{(x,y)}`` convention
    the first index varies within a row instead.
    """
    votes: Dict[str, List[int]] = {}
    prev_token = None

    for var_token in var_tokens:
        if (
            prev_token is not None
            and prev_token.var_name == var_token.var_name
            and prev_token.dim_num() >= 2
            and prev_token.dim_num() == var_token.dim_num()
        ):
            indices = (
                var_token.first_index,
                var_token.second_index,
                var_token.third_index,
            )
            prev_indices = (
                prev_token.first_index,
                prev_token.second_index,
                prev_token.third_index,
            )
            diffs = [
                current != prev
                for current, prev in zip(indices, prev_indices)
            ]

            if sum(diffs) == 1:
                var_votes = votes.setdefault(
                    var_token.var_name,
                    [0, 0, 0],
                )
                var_votes[diffs.index(True)] += 1

        prev_token = var_token

    return votes


def _predict_simple_format_main(
    var_tokens: List[VariableToken],
    to_1d_flag=False,
) -> Format[SimpleVariable]:
    # to_1d_flag collapses the dimension that a compact character row
    # represents as one string token.  ``"first"`` drops the last
    # (innermost) dimension, which is the common ``s_{i,j}`` convention
    # where the surviving index is the row.  ``"second"`` drops the
    # first (outermost) dimension for the transposed convention such as
    # ``c_{x,y}`` where the last index is the row.  ``"auto"`` decides
    # the dropped dimension per variable from which index varies
    # between adjacent occurrences.  ``True`` is accepted as a legacy
    # alias of ``"second"``.
    if to_1d_flag is True:
        to_1d_flag = "second"

    inner_dim_votes = None
    if to_1d_flag == "auto":
        inner_dim_votes = _vote_inner_dimensions(var_tokens)

    var_to_positions = {}
    var_to_simple_var = OrderedDict()

    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name

        if var_name not in var_to_simple_var:
            var_to_simple_var[var_name] = (
                SimpleVariable.create(
                    var_name,
                    var_token.dim_num(),
                )
            )
            var_to_positions[var_name] = []

        var_to_positions[var_name].append(pos)

        if var_token.dim_num() >= 3:
            var_to_simple_var[
                var_name
            ].third_index.update(
                var_token.third_index
            )

        if var_token.dim_num() >= 2:
            var_to_simple_var[
                var_name
            ].second_index.update(
                var_token.second_index
            )

        if var_token.dim_num() >= 1:
            var_to_simple_var[
                var_name
            ].first_index.update(
                var_token.first_index
            )

    already_processed_vars = set()
    root = Format()

    for pos, var_token in enumerate(var_tokens):
        var_name = var_token.var_name
        simple_var = var_to_simple_var[var_name]

        if var_name in already_processed_vars:
            continue

        dim = var_token.dim_num()

        if dim >= 2 and to_1d_flag:
            # Collapse the inner (varying) dimension that a compact
            # character row represents as one string token.
            if to_1d_flag == "first":
                drop_dim = dim - 1
            elif to_1d_flag == "second":
                drop_dim = 0
            else:
                var_votes = inner_dim_votes.get(var_name)
                if var_votes is None:
                    drop_dim = dim - 1
                else:
                    drop_dim = max(
                        range(dim),
                        key=lambda d: (
                            var_votes[d],
                            d,
                        ),
                    )

            kept = [
                simple_var.first_index,
                simple_var.second_index,
                simple_var.third_index,
            ][:dim]
            kept.pop(drop_dim)
            simple_var.first_index = kept[0]
            simple_var.second_index = (
                kept[1] if len(kept) > 1 else None
            )
            simple_var.third_index = None
            dim -= 1

        if dim == 0:
            root.push_back(
                SingularPattern(simple_var)
            )
            already_processed_vars.add(var_name)

        elif dim == 1:
            period = _predict_period(
                var_to_positions[var_name]
            )
            parallel_vars_group = [
                var_to_simple_var[token.var_name]
                for token in var_tokens[
                    pos:pos + period
                ]
            ]

            root.push_back(
                ParallelPattern(
                    parallel_vars_group
                )
            )

            for var in parallel_vars_group:
                already_processed_vars.add(
                    var.name
                )

        elif dim == 2:
            root.push_back(
                TwoDimensionalPattern(
                    simple_var
                )
            )
            already_processed_vars.add(var_name)

        elif dim == 3:
            root.push_back(
                ThreeDimensionalPattern(
                    simple_var
                )
            )
            already_processed_vars.add(var_name)

        else:
            raise NotImplementedError

    return root


def predict_simple_format(
    var_tokens: List[VariableToken],
    to_1d_flag=False,
) -> Format[SimpleVariable]:
    try:
        return _predict_simple_format_main(var_tokens, to_1d_flag)
    except (WrongGroupingError, UnknownPeriodError):
        raise SimpleFormatPredictionFailedError
