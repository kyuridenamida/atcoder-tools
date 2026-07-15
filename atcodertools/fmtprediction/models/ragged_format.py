from dataclasses import dataclass
from typing import Tuple

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

        if (
            self.length_field.type.value
            != "int"
        ):
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
