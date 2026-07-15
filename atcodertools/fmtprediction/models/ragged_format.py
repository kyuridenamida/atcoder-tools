from dataclasses import dataclass
from typing import Dict, Tuple

from atcodertools.fmtprediction.models.format import (
    Format,
)
from atcodertools.fmtprediction.models.type import (
    Type,
)


@dataclass(frozen=True)
class TypedRaggedField:
    name: str
    type: Type

    def __post_init__(self):
        if not self.name:
            raise ValueError(
                "ragged field name must not be empty"
            )


@dataclass(frozen=True)
class RaggedRowPattern:
    row_count_var: str
    prefix_fields: Tuple[
        TypedRaggedField,
        ...,
    ]
    length_field_position: int
    values_field: TypedRaggedField
    value_start_index: int

    def __post_init__(self):
        if not self.row_count_var:
            raise ValueError(
                "row count variable must not be empty"
            )

        if not self.prefix_fields:
            raise ValueError(
                "ragged prefix fields must not be empty"
            )

        if not (
            0
            <= self.length_field_position
            < len(self.prefix_fields)
        ):
            raise ValueError(
                "invalid ragged length field position"
            )

        if self.length_field.type.value != "int":
            raise ValueError(
                "ragged length field must be int"
            )

        names = [
            field.name
            for field in self.prefix_fields
        ]

        names.append(
            self.values_field.name
        )

        if len(names) != len(set(names)):
            raise ValueError(
                "ragged field names must be unique"
            )

        if self.value_start_index not in {
            0,
            1,
        }:
            raise ValueError(
                "ragged value start index must be 0 or 1"
            )

    @property
    def length_field(
        self,
    ) -> TypedRaggedField:
        return self.prefix_fields[
            self.length_field_position
        ]

    def all_fields(
        self,
    ) -> Tuple[TypedRaggedField, ...]:
        return (
            self.prefix_fields
            + (self.values_field,)
        )

    def __str__(self):
        return (
            "[RaggedRowPattern: count={}, "
            "prefix={}, length_pos={}, values={}]"
        ).format(
            self.row_count_var,
            ",".join(
                field.name
                for field in self.prefix_fields
            ),
            self.length_field_position,
            self.values_field.name,
        )


@dataclass(frozen=True)
class RaggedFieldVariable:
    name: str
    type: Type
    dimension: int

    first_index = None
    second_index = None
    third_index = None

    def dim_num(self):
        return self.dimension


class RaggedRowFormat(Format):
    def __init__(
        self,
        prefix_format,
        ragged_pattern,
        suffix_format=None,
    ):
        super().__init__()

        if suffix_format is None:
            suffix_format = Format()

        self.prefix_format = prefix_format
        self.ragged_pattern = ragged_pattern
        self.suffix_format = suffix_format

        self.sequence = (
            list(prefix_format.sequence)
            + list(suffix_format.sequence)
        )

        self.ragged_variables = tuple(
            [
                RaggedFieldVariable(
                    field.name,
                    field.type,
                    1,
                )
                for field
                in ragged_pattern.prefix_fields
            ]
            + [
                RaggedFieldVariable(
                    ragged_pattern.values_field.name,
                    ragged_pattern.values_field.type,
                    2,
                )
            ]
        )

    def all_vars(self):
        return (
            self.prefix_format.all_vars()
            + list(self.ragged_variables)
            + self.suffix_format.all_vars()
        )

    def __str__(self):
        return (
            "[RaggedRowFormat: prefix={}, "
            "rows={}, suffix={}]"
        ).format(
            self.prefix_format,
            self.ragged_pattern,
            self.suffix_format,
        )


def create_typed_ragged_row_pattern(
    schema,
    var_to_type: Dict[str, Type],
) -> RaggedRowPattern:
    prefix_fields = tuple(
        TypedRaggedField(
            name=name,
            type=var_to_type[name],
        )
        for name in schema.prefix_fields
    )

    values_field = TypedRaggedField(
        name=schema.values_name,
        type=var_to_type[
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
