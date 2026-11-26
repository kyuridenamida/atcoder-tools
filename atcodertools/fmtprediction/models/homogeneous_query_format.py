from dataclasses import dataclass
from typing import Tuple

from atcodertools.fmtprediction.models.format import (
    Format,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryArgument,
)


@dataclass(frozen=True)
class HomogeneousQueryFormat:
    prefix_format: Format
    query_count_var: str
    arguments: Tuple[
        TaggedQueryArgument,
        ...,
    ]
    query_collection_name: str = "queries"

    def __post_init__(self) -> None:
        if not self.arguments:
            raise ValueError(
                "homogeneous query arguments "
                "must not be empty"
            )

        names = [
            argument.name
            for argument in self.arguments
        ]

        if len(names) != len(set(names)):
            raise ValueError(
                "homogeneous query argument "
                "names must be unique"
            )

    @property
    def arity(self) -> int:
        return len(self.arguments)

    def all_vars(self):
        return self.prefix_format.all_vars()

    def __str__(self) -> str:
        arguments = ",".join(
            "{}:{}".format(
                argument.name,
                argument.type.value,
            )
            for argument in self.arguments
        )

        return (
            "[HomogeneousQueryFormat: "
            "prefix={}, count={}, arguments={}]"
        ).format(
            self.prefix_format,
            self.query_count_var,
            arguments,
        )
