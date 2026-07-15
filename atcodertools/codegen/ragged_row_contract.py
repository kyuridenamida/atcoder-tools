from dataclasses import dataclass
from typing import Mapping


class RaggedCodegenContractError(
    Exception
):
    pass


class RaggedCodegenContractNotFoundError(
    RaggedCodegenContractError
):
    pass


class InvalidRaggedCodegenContractError(
    RaggedCodegenContractError
):
    pass


_REQUIRED_KEYS = (
    "container_type",
    "declare",
    "allocate_outer",
    "declare_and_allocate_outer",
    "allocate_inner",
    "access",
)


@dataclass(frozen=True)
class RaggedCodegenContract:
    container_type_template: str
    declare_template: str
    allocate_outer_template: str
    declare_and_allocate_outer_template: str
    allocate_inner_template: str
    access_template: str

    @classmethod
    def from_mapping(
        cls,
        config: Mapping,
    ) -> "RaggedCodegenContract":
        ragged = config.get("ragged")

        if not isinstance(ragged, Mapping):
            raise (
                RaggedCodegenContractNotFoundError
            )

        missing = [
            key
            for key in _REQUIRED_KEYS
            if key not in ragged
        ]

        if missing:
            raise (
                InvalidRaggedCodegenContractError(
                    "missing ragged keys: {}"
                    .format(
                        ",".join(missing)
                    )
                )
            )

        return cls(
            container_type_template=str(
                ragged["container_type"]
            ),
            declare_template=str(
                ragged["declare"]
            ),
            allocate_outer_template=str(
                ragged["allocate_outer"]
            ),
            declare_and_allocate_outer_template=(
                str(
                    ragged[
                        "declare_and_allocate_outer"
                    ]
                )
            ),
            allocate_inner_template=str(
                ragged["allocate_inner"]
            ),
            access_template=str(
                ragged["access"]
            ),
        )

    @staticmethod
    def _render(
        template: str,
        values,
    ) -> str:
        try:
            return template.format(
                **values
            )
        except (
            IndexError,
            KeyError,
            ValueError,
        ) as error:
            raise (
                InvalidRaggedCodegenContractError(
                    "invalid ragged template: {}"
                    .format(error)
                )
            )

    def _values(
        self,
        *,
        name: str,
        type_: str,
        default: str,
        length_i: str,
        length_j: str,
        index_i: str,
        index_j: str,
    ):
        container_type = self._render(
            self.container_type_template,
            {
                "type": type_,
            },
        )

        return {
            "name": name,
            "type": type_,
            "default": default,
            "length_i": length_i,
            "length_j": length_j,
            "index_i": index_i,
            "index_j": index_j,
            "container_type": container_type,
        }

    def render_container_type(
        self,
        *,
        type_: str,
    ) -> str:
        return self._render(
            self.container_type_template,
            {
                "type": type_,
            },
        )

    def render_declare(
        self,
        **kwargs,
    ) -> str:
        return self._render(
            self.declare_template,
            self._values(**kwargs),
        )

    def render_allocate_outer(
        self,
        **kwargs,
    ) -> str:
        return self._render(
            self.allocate_outer_template,
            self._values(**kwargs),
        )

    def render_declare_and_allocate_outer(
        self,
        **kwargs,
    ) -> str:
        return self._render(
            (
                self
                .declare_and_allocate_outer_template
            ),
            self._values(**kwargs),
        )

    def render_allocate_inner(
        self,
        **kwargs,
    ) -> str:
        return self._render(
            self.allocate_inner_template,
            self._values(**kwargs),
        )

    def render_access(
        self,
        **kwargs,
    ) -> str:
        return self._render(
            self.access_template,
            self._values(**kwargs),
        )
