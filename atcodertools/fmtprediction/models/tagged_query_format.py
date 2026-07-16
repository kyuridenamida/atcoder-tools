from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

from atcodertools.fmtprediction.models.format import (
    Format,
)


class TaggedQueryValueType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "str"


@dataclass(frozen=True)
class TaggedQueryArgument:
    name: str
    type: TaggedQueryValueType


@dataclass(frozen=True)
class TaggedQueryVariant:
    tag: int
    arguments: Tuple[
        TaggedQueryArgument,
        ...,
    ]

    @property
    def arity(self) -> int:
        return len(self.arguments)


@dataclass(frozen=True)
class TaggedQueryFormat:
    prefix_format: Format
    query_count_var: str
    variants: Tuple[
        TaggedQueryVariant,
        ...,
    ]
    query_collection_name: str = "queries"

    def __post_init__(self) -> None:
        if not self.variants:
            raise ValueError(
                "tagged query variants must not be empty"
            )

        tags = [
            variant.tag
            for variant in self.variants
        ]

        if tags != sorted(tags):
            raise ValueError(
                "tagged query variants must be sorted"
            )

        if len(tags) != len(set(tags)):
            raise ValueError(
                "tagged query tags must be unique"
            )

    @property
    def variants_by_tag(
        self,
    ) -> Dict[int, TaggedQueryVariant]:
        return {
            variant.tag: variant
            for variant in self.variants
        }

    def __str__(self) -> str:
        variants = ",".join(
            "{}:{}".format(
                variant.tag,
                [
                    argument.type.value
                    for argument in variant.arguments
                ],
            )
            for variant in self.variants
        )

        return (
            "[TaggedQueryFormat: "
            "prefix={}, count={}, variants={}]"
        ).format(
            self.prefix_format,
            self.query_count_var,
            variants,
        )
