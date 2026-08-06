from dataclasses import dataclass
import json
import re
from typing import Dict, Optional

from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
    TaggedQueryValueType,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


@dataclass(frozen=True)
class _StoredField:
    variable: Variable
    local_name: str
    value_type: TaggedQueryValueType
    tag: Optional[object]


class UniversalQueryCodeGenerator:
    """Portable query codegen based on parallel typed arrays.

    Input is fully materialized before ``solve`` is called.  This preserves
    atcoder-tools' testability contract: callers may construct the arrays
    directly and call ``solve`` without standard input.
    """

    _BLOCK_LANGUAGES = {
        "cpp",
        "cs",
        "d",
        "go",
        "java",
        "rust",
        "swift",
    }

    def __init__(self, parent):
        self._parent = parent
        self._format = parent._format
        self._language = parent._generator_path.stem
        if self._language not in {
            "cpp",
            "cs",
            "d",
            "go",
            "java",
            "julia",
            "nim",
            "python",
            "rust",
            "swift",
        }:
            raise ValueError(
                "unsupported universal query language: {}".format(
                    self._language
                )
            )

    @staticmethod
    def _type(value_type):
        return getattr(Type, value_type.value)

    @staticmethod
    def _safe_component(value):
        symbolic_names = {
            "+": "plus",
            "-": "minus",
            "?": "question",
            "!": "bang",
        }
        if isinstance(value, int):
            return "number_{}".format(value)
        if value in symbolic_names:
            return "symbol_{}".format(
                symbolic_names[value]
            )
        result = re.sub(
            r"[^A-Za-z0-9_]+",
            "_",
            str(value),
        ).strip("_")
        if not result:
            result = "value"
        return "word_{}".format(result.lower())

    @staticmethod
    def _safe_local(name):
        common_reserved = {
            "as",
            "case",
            "class",
            "default",
            "else",
            "enum",
            "false",
            "for",
            "func",
            "function",
            "if",
            "in",
            "let",
            "match",
            "nil",
            "none",
            "null",
            "return",
            "struct",
            "switch",
            "true",
            "type",
            "var",
            "while",
        }
        if name.lower() in common_reserved:
            return "query_" + name
        return name

    def _index(self):
        index = Index()
        index.update("1")
        index.update(self._format.query_count_var)
        return index

    def _variable(self, name, value_type):
        return Variable(
            name,
            self._index(),
            None,
            self._type(value_type),
        )

    def _actual_argument(self, variable):
        if variable.dim_num() == 0:
            return variable.name
        kind = self._parent._get_variable_kind(variable)
        if (
            "actual_arg" in self._parent.info
            and kind in self._parent.info["actual_arg"]
        ):
            return self._parent.info["actual_arg"][kind].format(
                name=variable.name
            )
        return variable.name

    def _prefix_formal_arguments(self):
        return [
            self._parent._get_argument(variable)
            for variable in self._format.prefix_format.all_vars()
        ]

    def _prefix_actual_arguments(self):
        return [
            self._actual_argument(variable)
            for variable in self._format.prefix_format.all_vars()
        ]

    def _prefix_global_declaration(self):
        lines = []
        for variable in self._format.prefix_format.all_vars():
            lines.append(
                self._parent.info["global_prefix"]
                + self._parent._generate_declaration(variable)
            )
        return "\n".join(line for line in lines if line)

    def _stored_fields(self):
        collection = self._format.query_collection_name
        fields = []
        tag_variable = None
        if isinstance(self._format, TaggedQueryFormat):
            tag_type = (
                TaggedQueryValueType.STRING
                if isinstance(self._format.variants[0].tag, str)
                else TaggedQueryValueType.INT
            )
            tag_variable = self._variable(
                collection + "_tag",
                tag_type,
            )
            for variant in self._format.variants:
                tag_component = self._safe_component(variant.tag)
                for argument in variant.arguments:
                    fields.append(
                        _StoredField(
                            variable=self._variable(
                                "{}_{}_{}".format(
                                    collection,
                                    tag_component,
                                    argument.name,
                                ),
                                argument.type,
                            ),
                            local_name=self._safe_local(
                                argument.name
                            ),
                            value_type=argument.type,
                            tag=variant.tag,
                        )
                    )
        else:
            for argument in self._format.arguments:
                fields.append(
                    _StoredField(
                        variable=self._variable(
                            "{}_{}".format(
                                collection,
                                argument.name,
                            ),
                            argument.type,
                        ),
                        local_name=self._safe_local(
                            argument.name
                        ),
                        value_type=argument.type,
                        tag=None,
                    )
                )
        return tag_variable, tuple(fields)

    def _literal(self, value):
        if isinstance(value, int):
            return str(value)
        return json.dumps(value)

    def _access(self, variable):
        return self._parent.info["access"]["seq"].format(
            name=variable.name,
            index=self._parent.info["index"]["i"],
        )

    def _condition_header(self, condition, first):
        if self._language == "python":
            return ("if" if first else "elif") + " " + condition + ":"
        if self._language == "nim":
            return ("if" if first else "elif") + " " + condition + ":"
        if self._language == "julia":
            return ("if" if first else "elseif") + " " + condition
        if self._language == "go":
            prefix = "if " if first else "} else if "
            return prefix + condition + " {"
        if self._language in {"rust", "swift"}:
            prefix = "if " if first else "} else if "
            return prefix + condition + " {"
        prefix = "if (" if first else "} else if ("
        return prefix + condition + ") {"

    def _else_header(self):
        if self._language in {"python", "nim"}:
            return "else:"
        if self._language == "julia":
            return "else"
        return "} else {"

    def _chain_footer(self):
        if self._language == "julia":
            return "end"
        if self._language in self._BLOCK_LANGUAGES:
            return "}"
        return ""

    def _unknown_tag_statement(self):
        return {
            "cpp": 'throw std::runtime_error("unknown query tag");',
            "cs": 'throw new System.ArgumentException("unknown query tag");',
            "d": 'throw new Exception("unknown query tag");',
            "go": 'panic("unknown query tag")',
            "java": 'throw new IllegalArgumentException("unknown query tag");',
            "julia": 'error("unknown query tag")',
            "nim": 'raise newException(ValueError, "unknown query tag")',
            "python": 'raise ValueError("unknown query tag")',
            "rust": 'panic!("unknown query tag");',
            "swift": 'fatalError("unknown query tag")',
        }[self._language]

    def _empty_statement(self):
        return {
            "python": "pass",
            "nim": "discard",
            "julia": "nothing",
        }.get(self._language, "")

    def _local_binding(self, field):
        access = self._access(field.variable)
        name = field.local_name
        if self._language == "cpp":
            return [
                "const auto {} = {};".format(name, access),
                "(void){};".format(name),
            ]
        if self._language == "cs":
            return [
                "var {} = {};".format(name, access),
                "_ = {};".format(name),
            ]
        if self._language == "d":
            return [
                "auto {} = {};".format(name, access),
                "cast(void) {};".format(name),
            ]
        if self._language == "go":
            return [
                "{} := {}".format(name, access),
                "_ = {}".format(name),
            ]
        if self._language == "java":
            return [
                "final {} {} = {};".format(
                    self._parent._convert_type(
                        self._type(field.value_type)
                    ),
                    name,
                    access,
                )
            ]
        if self._language == "julia":
            return ["{} = {}".format(name, access)]
        if self._language == "nim":
            return [
                "let {} = {}".format(name, access),
                "discard {}".format(name),
            ]
        if self._language == "python":
            return ["{} = {}".format(name, access)]
        if self._language == "rust":
            if field.value_type == TaggedQueryValueType.STRING:
                access = "&" + access
            return [
                "let {} = {};".format(name, access),
                "let _ = &{};".format(name),
            ]
        if self._language == "swift":
            return [
                "let {} = {}".format(name, access),
                "_ = {}".format(name),
            ]
        raise AssertionError(self._language)

    def _todo_statement(self):
        if self._language in {"python", "nim", "julia"}:
            return "# TODO: process this query variant"
        return "// TODO: process this query variant"

    def _tag_condition(self, tag_access, tag):
        literal = self._literal(tag)
        if self._language == "java" and isinstance(tag, str):
            return "{}.equals({})".format(
                literal,
                tag_access,
            )
        return "{} == {}".format(tag_access, literal)

    def _append_tagged_chain(
        self,
        lines,
        tag_variable,
        fields,
        *,
        input_mode,
        base_indent,
    ):
        tag_access = self._access(tag_variable)
        for variant_index, variant in enumerate(
            self._format.variants
        ):
            condition = self._tag_condition(
                tag_access,
                variant.tag,
            )
            self._parent._append(
                lines,
                self._condition_header(
                    condition,
                    variant_index == 0,
                ),
                base_indent,
            )
            selected = [
                field
                for field in fields
                if field.tag == variant.tag
            ]
            statements = []
            if input_mode:
                statements = [
                    self._parent._input_code_for_var(
                        field.variable
                    )
                    for field in selected
                ]
            else:
                for field in selected:
                    statements.extend(
                        self._local_binding(field)
                    )
                statements.append(self._todo_statement())
                if not selected:
                    empty = self._empty_statement()
                    if empty:
                        statements.append(empty)
            if not statements:
                statements = [self._empty_statement()]
            for statement in statements:
                if statement:
                    self._parent._append(
                        lines,
                        statement,
                        base_indent + 1,
                    )
        self._parent._append(
            lines,
            self._else_header(),
            base_indent,
        )
        self._parent._append(
            lines,
            self._unknown_tag_statement(),
            base_indent + 1,
        )
        footer = self._chain_footer()
        if footer:
            self._parent._append(
                lines,
                footer,
                base_indent,
            )

    def _query_lines(self, *, global_mode):
        tag_variable, fields = self._stored_fields()
        variables = (
            ([tag_variable] if tag_variable is not None else [])
            + [field.variable for field in fields]
        )
        lines = []
        for variable in variables:
            if global_mode:
                code = self._parent._generate_allocation(
                    variable
                )
            else:
                code = (
                    self._parent
                    ._generate_declaration_and_allocation(
                        variable
                    )
                )
            self._parent._append(lines, code)
        representative = variables[0]
        self._parent._append(
            lines,
            self._parent._loop_header(
                representative,
                False,
            ),
        )
        if tag_variable is not None:
            self._parent._append(
                lines,
                self._parent._input_code_for_var(
                    tag_variable
                ),
                1,
            )
            self._append_tagged_chain(
                lines,
                tag_variable,
                fields,
                input_mode=True,
                base_indent=1,
            )
        else:
            for field in fields:
                self._parent._append(
                    lines,
                    self._parent._input_code_for_var(
                        field.variable
                    ),
                    1,
                )
        self._parent._append(
            lines,
            self._parent.info["loop"]["footer"].format(
                loop_var=self._parent.info["index"]["i"]
            ),
        )
        return lines, variables

    def _dispatch_skeleton(self):
        tag_variable, fields = self._stored_fields()
        variables = (
            ([tag_variable] if tag_variable is not None else [])
            + [field.variable for field in fields]
        )
        lines = []
        self._parent._append(
            lines,
            self._parent._loop_header(
                variables[0],
                False,
            ),
        )
        if tag_variable is not None:
            self._append_tagged_chain(
                lines,
                tag_variable,
                fields,
                input_mode=False,
                base_indent=1,
            )
        else:
            for field in fields:
                for statement in self._local_binding(field):
                    self._parent._append(
                        lines,
                        statement,
                        1,
                    )
            self._parent._append(
                lines,
                self._todo_statement(),
                1,
            )
        self._parent._append(
            lines,
            self._parent.info["loop"]["footer"].format(
                loop_var=self._parent.info["index"]["i"]
            ),
        )
        return self._parent._render_input_lines(lines)

    @staticmethod
    def _join(*parts):
        return "\n".join(part for part in parts if part)

    def generate_parameters(self) -> Dict[str, object]:
        query_lines, variables = self._query_lines(
            global_mode=False
        )
        global_query_lines, _ = self._query_lines(
            global_mode=True
        )
        prefix_input = self._parent._get_input_part(
            global_mode=False,
            format_=self._format.prefix_format,
            include_prefix=True,
        )
        prefix_global_input = self._parent._get_input_part(
            global_mode=True,
            format_=self._format.prefix_format,
            include_prefix=True,
        )
        query_input = self._parent._render_input_lines(
            query_lines
        )
        global_query_input = (
            self._parent._render_input_lines(
                global_query_lines
            )
        )
        formal_arguments = self._prefix_formal_arguments()
        formal_arguments.extend(
            self._parent._get_argument(variable)
            for variable in variables
        )
        actual_arguments = self._prefix_actual_arguments()
        actual_arguments.extend(
            self._actual_argument(variable)
            for variable in variables
        )
        query_global_declarations = []
        for variable in variables:
            declaration = self._parent._generate_declaration(
                variable
            )
            if declaration:
                query_global_declarations.append(
                    self._parent.info["global_prefix"]
                    + declaration
                )
        is_tagged = isinstance(
            self._format,
            TaggedQueryFormat,
        )
        return {
            "formal_arguments": ", ".join(
                formal_arguments
            ),
            "actual_arguments": ", ".join(
                actual_arguments
            ),
            "input_part": self._join(
                prefix_input,
                query_input,
            ),
            "prefix_input_part": prefix_input,
            "case_input_part": "",
            "global_declaration": self._join(
                self._prefix_global_declaration(),
                "\n".join(query_global_declarations),
            ),
            "global_input_part": self._join(
                prefix_global_input,
                global_query_input,
            ),
            "multi_case": False,
            "case_count_var": None,
            "case_loop_var": None,
            "tagged_query": is_tagged,
            "homogeneous_query": not is_tagged,
            "query_dispatch_skeleton": (
                self._dispatch_skeleton()
            ),
            "query_storage_names": tuple(
                variable.name for variable in variables
            ),
            "prediction_success": True,
        }
