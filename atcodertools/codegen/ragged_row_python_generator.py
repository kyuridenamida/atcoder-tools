from dataclasses import dataclass
from typing import Iterable, Tuple

from atcodertools.fmtprediction.models.ragged_format import (
    RaggedRowPattern,
    TypedRaggedField,
)
from atcodertools.fmtprediction.ragged_row import (
    SameLineRaggedRowPrediction,
)


class UnsupportedRaggedPythonTypeError(
    Exception
):
    pass


@dataclass(frozen=True)
class RaggedRowPythonCode:
    pattern: RaggedRowPattern
    declarations: str
    input_part: str
    actual_arguments: Tuple[str, ...]

    def render(self) -> str:
        parts = [
            part
            for part in (
                self.declarations,
                self.input_part,
            )
            if part
        ]

        return "\n".join(parts)


def _type_value(type_) -> str:
    return str(type_.value)


def _python_default(type_) -> str:
    value = _type_value(type_)

    if value == "int":
        return "0"

    if value == "float":
        return "0.0"

    if value in {
        "str",
        "string",
        "char",
    }:
        return '""'

    raise UnsupportedRaggedPythonTypeError(
        value
    )


def _python_scalar_expression(
    type_,
    source: str,
) -> str:
    value = _type_value(type_)

    if value == "int":
        return "int({})".format(source)

    if value == "float":
        return "float({})".format(source)

    if value in {
        "str",
        "string",
        "char",
    }:
        return source

    raise UnsupportedRaggedPythonTypeError(
        value
    )


def _python_list_expression(
    type_,
    source: str,
) -> str:
    value = _type_value(type_)

    if value == "int":
        return "list(map(int, {}))".format(
            source
        )

    if value == "float":
        return "list(map(float, {}))".format(
            source
        )

    if value in {
        "str",
        "string",
        "char",
    }:
        return "list({})".format(source)

    raise UnsupportedRaggedPythonTypeError(
        value
    )


def _unique_internal_name(
    base: str,
    used_names: Iterable[str],
) -> str:
    used = set(used_names)

    candidate = base

    while candidate in used:
        candidate += "_"

    return candidate


def build_typed_ragged_row_pattern(
    prediction: SameLineRaggedRowPrediction,
) -> RaggedRowPattern:
    schema = prediction.schema

    prefix_fields = tuple(
        TypedRaggedField(
            name=name,
            type=prediction.var_to_type[name],
        )
        for name in schema.prefix_fields
    )

    values_field = TypedRaggedField(
        name=schema.values_name,
        type=prediction.var_to_type[
            schema.values_name
        ],
    )

    return RaggedRowPattern(
        row_count_var=schema.row_count_var,
        prefix_fields=prefix_fields,
        length_field_position=(
            schema.length_field_position
        ),
        values_field=values_field,
        value_start_index=(
            schema.value_start_index
        ),
    )


def generate_same_line_ragged_row_python(
    prediction: SameLineRaggedRowPrediction,
    *,
    validate_length: bool = True,
) -> RaggedRowPythonCode:
    pattern = build_typed_ragged_row_pattern(
        prediction
    )

    field_names = [
        field.name
        for field in pattern.all_fields()
    ]

    used_names = set(field_names)
    used_names.add(
        pattern.row_count_var
    )

    loop_var = _unique_internal_name(
        "_ragged_i",
        used_names,
    )

    used_names.add(loop_var)

    row_var = _unique_internal_name(
        "_ragged_row",
        used_names,
    )

    declarations = []

    for field in pattern.prefix_fields:
        declarations.append(
            "{} = [{}] * {}".format(
                field.name,
                _python_default(field.type),
                pattern.row_count_var,
            )
        )

    declarations.append(
        "{} = [[] for _ in range({})]".format(
            pattern.values_field.name,
            pattern.row_count_var,
        )
    )

    lines = [
        "for {} in range({}):".format(
            loop_var,
            pattern.row_count_var,
        ),
        "    {} = input().split()".format(
            row_var
        ),
    ]

    for index, field in enumerate(
        pattern.prefix_fields
    ):
        expression = (
            _python_scalar_expression(
                field.type,
                "{}[{}]".format(
                    row_var,
                    index,
                ),
            )
        )

        lines.append(
            "    {}[{}] = {}".format(
                field.name,
                loop_var,
                expression,
            )
        )

    values_source = "{}[{}:]".format(
        row_var,
        len(pattern.prefix_fields),
    )

    lines.append(
        "    {}[{}] = {}".format(
            pattern.values_field.name,
            loop_var,
            _python_list_expression(
                pattern.values_field.type,
                values_source,
            ),
        )
    )

    if validate_length:
        lines.extend(
            [
                (
                    "    if len({values}[{index}]) "
                    "!= {length}[{index}]:"
                ).format(
                    values=(
                        pattern.values_field.name
                    ),
                    length=(
                        pattern.length_field.name
                    ),
                    index=loop_var,
                ),
                (
                    "        raise ValueError("
                    '"ragged row length mismatch"'
                    ")"
                ),
            ]
        )

    return RaggedRowPythonCode(
        pattern=pattern,
        declarations="\n".join(
            declarations
        ),
        input_part="\n".join(lines),
        actual_arguments=tuple(field_names),
    )
