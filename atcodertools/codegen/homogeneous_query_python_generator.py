from pathlib import Path
from typing import List

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryValueType,
)


class HomogeneousQueryPythonGenerator:
    def __init__(
        self,
        format_: HomogeneousQueryFormat,
        prefix_input_part: str,
    ):
        self._format = format_
        self._prefix_input_part = (
            prefix_input_part
        )

    @classmethod
    def from_universal_generator(
        cls,
        format_: HomogeneousQueryFormat,
        config,
        python_toml_path: Path,
    ):
        generator = UniversalCodeGenerator(
            format_.prefix_format,
            config,
            python_toml_path,
        )

        parameters = (
            generator.generate_parameters()
        )

        if not parameters[
            "prediction_success"
        ]:
            raise ValueError(
                "prefix generation failed"
            )

        return cls(
            format_,
            parameters["input_part"],
        )

    @staticmethod
    def _indent_text(
        text: str,
        indent: str,
    ) -> List[str]:
        return [
            (
                indent + line
                if line
                else line
            )
            for line in text.splitlines()
        ]

    @staticmethod
    def _cast_expression(
        type_: TaggedQueryValueType,
        expression: str,
    ) -> str:
        if type_ == TaggedQueryValueType.INT:
            return "int({})".format(
                expression
            )

        if (
            type_
            == TaggedQueryValueType.FLOAT
        ):
            return "float({})".format(
                expression
            )

        return expression

    def generate_input_part(
        self,
        indent: str = "",
    ) -> str:
        lines = self._indent_text(
            self._prefix_input_part,
            indent,
        )

        body_indent = indent + " " * 4
        collection = (
            self._format
            .query_collection_name
        )

        lines.append(
            "{}{} = []".format(
                indent,
                collection,
            )
        )

        lines.append(
            "{}for _query_index in "
            "range({}):".format(
                indent,
                self._format
                .query_count_var,
            )
        )

        lines.append(
            "{}_query_parts = "
            "input().split()".format(
                body_indent
            )
        )

        lines.append(
            "{}if len(_query_parts) "
            "!= {}:".format(
                body_indent,
                self._format.arity,
            )
        )

        lines.append(
            "{}raise ValueError("
            "'invalid query arity')".format(
                body_indent + " " * 4
            )
        )

        tuple_items = []

        for position, argument in enumerate(
            self._format.arguments
        ):
            variable_name = (
                "_query_arg_{}"
                .format(position)
            )

            expression = (
                "_query_parts[{}]"
                .format(position)
            )

            lines.append(
                "{}{} = {}".format(
                    body_indent,
                    variable_name,
                    self._cast_expression(
                        argument.type,
                        expression,
                    ),
                )
            )

            tuple_items.append(
                variable_name
            )

        if len(tuple_items) == 1:
            tuple_expression = "({},)".format(
                tuple_items[0]
            )
        else:
            tuple_expression = "({})".format(
                ", ".join(tuple_items)
            )

        lines.append(
            "{}{}.append({})".format(
                body_indent,
                collection,
                tuple_expression,
            )
        )

        return "\n".join(lines)
