import keyword
from pathlib import Path
from typing import List

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
    TaggedQueryValueType,
)


class TaggedQueryPythonGenerator:
    def __init__(
        self,
        format_: TaggedQueryFormat,
        prefix_input_part: str,
    ):
        self._format = format_
        self._prefix_input_part = (
            prefix_input_part
        )

    @classmethod
    def from_universal_generator(
        cls,
        format_: TaggedQueryFormat,
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

    @staticmethod
    def _safe_local(name: str) -> str:
        if keyword.iskeyword(name):
            return "_query_" + name
        return name

    def generate_dispatch_skeleton(
        self,
        indent: str = "    ",
    ) -> str:
        collection = self._format.query_collection_name
        body_indent = indent + " " * 4
        variant_indent = body_indent + " " * 4
        lines = [
            "{}for _query in {}:".format(
                indent,
                collection,
            ),
            "{}_query_tag = _query[0]".format(
                body_indent
            ),
        ]
        for index, variant in enumerate(
            self._format.variants
        ):
            keyword_ = "if" if index == 0 else "elif"
            lines.append(
                "{}{} _query_tag == {}:".format(
                    body_indent,
                    keyword_,
                    repr(variant.tag),
                )
            )
            if variant.arguments:
                names = ["_"] + [
                    self._safe_local(argument.name)
                    for argument in variant.arguments
                ]
                lines.append(
                    "{}{} = _query".format(
                        variant_indent,
                        ", ".join(names),
                    )
                )
            lines.append(
                "{}# TODO: process this query variant".format(
                    variant_indent
                )
            )
            if not variant.arguments:
                lines.append(
                    "{}pass".format(variant_indent)
                )
        lines.extend([
            "{}else:".format(body_indent),
            "{}raise ValueError("
            "\"unknown query tag\")".format(
                variant_indent
            ),
        ])
        return "\n".join(lines)

    def generate_input_part(
        self,
        indent: str = "",
    ) -> str:
        lines = self._indent_text(
            self._prefix_input_part,
            indent,
        )

        body_indent = indent + " " * 4
        variant_indent = body_indent + " " * 4
        collection = self._format.query_collection_name
        lines.append(
            "{}{} = []".format(indent, collection)
        )
        lines.append(
            "{}for _query_index in range({}):".format(
                indent,
                self._format.query_count_var,
            )
        )
        lines.append(
            "{}_query_parts = input().split()".format(
                body_indent
            )
        )
        lines.append(
            "{}if not _query_parts:".format(
                body_indent
            )
        )
        lines.append(
            "{}raise ValueError("
            "'empty query row')".format(
                variant_indent
            )
        )
        string_tags = isinstance(
            self._format.variants[0].tag,
            str,
        )
        tag_expression = (
            "_query_parts[0]"
            if string_tags
            else "int(_query_parts[0])"
        )
        lines.append(
            "{}_query_tag = {}".format(
                body_indent,
                tag_expression,
            )
        )
        for index, variant in enumerate(
            self._format.variants
        ):
            keyword_ = "if" if index == 0 else "elif"
            lines.append(
                "{}{} _query_tag == {}:".format(
                    body_indent,
                    keyword_,
                    repr(variant.tag),
                )
            )
            lines.append(
                "{}if len(_query_parts) != {}:".format(
                    variant_indent,
                    variant.arity + 1,
                )
            )
            lines.append(
                "{}raise ValueError("
                "'invalid query arity')".format(
                    variant_indent + " " * 4
                )
            )
            tuple_items = ["_query_tag"]
            for position, argument in enumerate(
                variant.arguments,
                start=1,
            ):
                variable_name = "_query_arg_{}".format(
                    position - 1
                )
                expression = "_query_parts[{}]".format(
                    position
                )
                lines.append(
                    "{}{} = {}".format(
                        variant_indent,
                        variable_name,
                        self._cast_expression(
                            argument.type,
                            expression,
                        ),
                    )
                )
                tuple_items.append(variable_name)
            tuple_expression = (
                "(_query_tag,)"
                if len(tuple_items) == 1
                else "({})".format(
                    ", ".join(tuple_items)
                )
            )
            lines.append(
                "{}{}.append({})".format(
                    variant_indent,
                    collection,
                    tuple_expression,
                )
            )
        lines.append("{}else:".format(body_indent))
        lines.append(
            "{}raise ValueError("
            "'unknown query tag: {}'"
            ".format(_query_tag))".format(
                variant_indent,
                "{}",
            )
        )
        return "\n".join(lines)
