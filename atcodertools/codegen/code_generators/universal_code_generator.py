# -*- coding: utf-8 -*-
from atcodertools.codegen.universal_query_codegen import (
    UniversalQueryCodeGenerator,
)
from typing import Dict, Any, Optional
import re

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.fmtprediction.models.format import (
    Format,
    ParallelPattern,
    Pattern,
    RepeatedCaseFormat,
    SingularPattern,
    ThreeDimensionalPattern,
    TwoDimensionalPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from pathlib import Path
import toml
from atcodertools.fmtprediction.models.ragged_format import (
    RaggedRowFormat,
)
from atcodertools.codegen.ragged_row_contract import (
    RaggedCodegenContract,
)
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
)


class UniversalCodeGenerator():
    def __init__(
        self,
        format_: Optional[Format[Variable]],
        config: CodeStyleConfig,
        path,
    ):
        super(UniversalCodeGenerator, self).__init__()

        self._format = format_
        self._config = config
        self._generator_path = Path(path)
        self.info = toml.load(path)

        if "index" not in self.info:
            self.info["index"] = {
                "i": "i",
                "j": "j",
            }

        self.info.setdefault("index", {})
        self.info["index"].setdefault("i", "i")
        self.info["index"].setdefault("j", "j")
        self.info["index"].setdefault("k", "k")
        self._prefix_format = format_
        self._solve_format = format_
        self._case_count_var = None
        self._case_loop_var = None
        self._ragged_format = None

        if isinstance(format_, RaggedRowFormat):
            self._ragged_format = format_
            self._prefix_format = (
                format_.prefix_format
            )
            self._solve_format = format_

        elif isinstance(format_, RepeatedCaseFormat):
            self._prefix_format = format_.prefix_format
            self._solve_format = format_.case_format
            self._case_count_var = format_.case_count_var
            self._case_loop_var = (
                self._choose_case_loop_var()
            )

    def _get_length(self, index) -> str:
        return self._insert_space_around_operators(str(index.get_length()))

    def _loop_header(
        self,
        var: Variable,
        for_second_index: bool,
        for_third_index: bool = False,
    ):
        if for_third_index:
            index = var.third_index
            loop_var = self.info["index"]["k"]
        elif for_second_index:
            index = var.second_index
            loop_var = self.info["index"]["j"]
        else:
            index = var.first_index
            loop_var = self.info["index"]["i"]

        return self.info["loop"]["header"].format(
            loop_var=loop_var,
            length=self._get_length(index),
        )

    def _insert_space_around_operators(self, code: str):
        if not self.info["insert_space_around_operators"]:
            return code
        precode = code
        pattern = r"([0-9a-zA-Z_])([+\-\*/])([0-9a-zA-Z_])"
        code = re.sub(pattern, r"\1 \2 \3", code)
        while precode != code:
            precode = code
            code = re.sub(pattern, r"\1 \2 \3", code)
        return code

    def _global_declaration(self) -> str:
        lines = []

        for pattern in self._solve_format.sequence:
            for var in pattern.all_vars():
                self._append(
                    lines,
                    (
                        self.info["global_prefix"]
                        + self._generate_declaration(var)
                    ),
                )

        return "\n".join(lines)

    def generate_parameters(self) -> Dict[str, Any]:
        if self._format is None:
            return dict(prediction_success=False)

        if isinstance(
            self._format,
            (
                TaggedQueryFormat,
                HomogeneousQueryFormat,
            ),
        ):
            return UniversalQueryCodeGenerator(
                self
            ).generate_parameters()

        if self._ragged_format is not None:
            return self._generate_ragged_parameters()

        input_part = self._input_part(
            global_mode=False
        )

        parameters = dict(
            formal_arguments=self._formal_arguments(),
            actual_arguments=self._actual_arguments(),
            input_part=input_part,
            prefix_input_part=self._get_input_part(
                global_mode=False,
                format_=self._prefix_format,
                include_prefix=True,
            ),
            case_input_part=self._get_input_part(
                global_mode=False,
                format_=self._solve_format,
                include_prefix=(
                    self._case_count_var is None
                ),
            ),
            global_declaration=self._global_declaration(),
            global_input_part=self._get_input_part(
                global_mode=True,
                format_=self._solve_format,
                include_prefix=True,
            ),
            multi_case=(
                self._case_count_var is not None
            ),
            case_count_var=self._case_count_var,
            case_loop_var=self._case_loop_var,
            prediction_success=True,
        )

        return parameters

    def _input_part(self, global_mode):
        return self._get_input_part(
            global_mode=global_mode,
            format_=self._solve_format,
            include_prefix=True,
        )

    def _get_input_part(
        self,
        global_mode,
        format_,
        include_prefix=True,
    ):
        lines = []

        newline_after_input = (
            "newline_after_input" in self.info
            and self.info["newline_after_input"]
        )

        if (
            include_prefix
            and "input_part_prefix" in self.info
        ):
            lines.extend(
                self.info["input_part_prefix"].split(
                    "\n"
                )
            )

        if newline_after_input and lines:
            lines.append("")

        for pattern in format_.sequence:
            lines += self._render_pattern(
                pattern,
                global_mode,
            )

            # Preserve the existing language-specific layout contract.
            # D, for example, requests a blank line after each input
            # declaration-and-read pattern.
            if newline_after_input:
                lines.append("")

        result = ""
        prefix = self._indent(
            self.info["base_indent"]
        )
        start = True

        for index, line in enumerate(lines):
            if len(line) > 0:
                if not start:
                    result += prefix

                result += line

            if index < len(lines) - 1:
                result += "\n"

            start = False

        return result

    def _choose_case_loop_var(self):
        used_names = set()

        for format_ in (
            self._prefix_format,
            self._solve_format,
        ):
            if format_ is None:
                continue

            used_names.update(
                variable.name
                for variable in format_.all_vars()
            )

        used_names.update(
            self.info.get(
                "index",
                {},
            ).values()
        )

        candidate = "case_index"

        while candidate in used_names:
            candidate = "_" + candidate

        return candidate

    def _convert_type(self, type_: Type) -> str:
        return self.info["type"][type_.value]

    def _default_val(self, type_: Type) -> str:
        return self.info["default"][type_.value]

    def _get_input_func(self, type_: Type) -> str:
        return self.info["input_func"][type_.value]

    def _get_format_keywords(
        self,
        var: Variable,
    ) -> dict:
        result = {
            "name": var.name,
            "type": self._convert_type(var.type),
            "default": self._default_val(var.type),
        }

        if "input_func" in self.info:
            result["input_func"] = (
                self._get_input_func(var.type)
            )

        if var.dim_num() == 0:
            pass
        elif var.dim_num() == 1:
            result["length"] = self._get_length(
                var.first_index
            )
        elif var.dim_num() == 2:
            result.update(
                {
                    "length_i": self._get_length(
                        var.first_index
                    ),
                    "length_j": self._get_length(
                        var.second_index
                    ),
                }
            )
        elif var.dim_num() == 3:
            result.update(
                {
                    "length_i": self._get_length(
                        var.first_index
                    ),
                    "length_j": self._get_length(
                        var.second_index
                    ),
                    "length_k": self._get_length(
                        var.third_index
                    ),
                }
            )
        else:
            raise NotImplementedError

        return result

    def _get_variable_kind(
        self,
        var: Variable,
    ) -> str:
        if var.dim_num() == 0:
            return var.type.value
        if var.dim_num() == 1:
            return "seq"
        if var.dim_num() == 2:
            return "2d_seq"
        if var.dim_num() == 3:
            return "3d_seq"

        raise NotImplementedError

    def _get_argument(self, var: Variable):
        kwd = self._get_format_keywords(var)
        kind = self._get_variable_kind(var)
        return self.info["arg"][kind].format(**kwd)

    def _actual_arguments(self) -> str:
        """
        Return actual solve-function arguments, e.g. ``N, K, a``.
        """
        result = []

        for variable in self._solve_format.all_vars():
            if variable.dim_num() == 0:
                result.append(variable.name)
            else:
                kind = self._get_variable_kind(
                    variable
                )

                if "actual_arg" in self.info:
                    result.append(
                        self.info["actual_arg"][
                            kind
                        ].format(
                            name=variable.name
                        )
                    )
                else:
                    result.append(variable.name)

        return ", ".join(result)

    def _formal_arguments(self):
        """
        Return formal solve-function arguments.
        """
        return ", ".join(
            self._get_argument(variable)
            for variable
            in self._solve_format.all_vars()
        )

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> \
std::vector<int> array = std::vector<int>(n-1+1);
        """
        kwd = self._get_format_keywords(var)
        kind = self._get_variable_kind(var)
        return self.info["declare"][kind].format(**kwd)

    def _generate_allocation(self, var: Variable):
        """
        :return: Create allocation part E.g. array[1..n] -> \
std::vector<int> array = std::vector<int>(n-1+1);
        """
        # ほとんどの言語ではint, float, stringは宣言したら確保もされるはず、そうでない言語だったらこれだとまずそう
        if var.dim_num() == 0:
            return ""
        else:
            kwd = self._get_format_keywords(var)
            kind = self._get_variable_kind(var)
            return self.info["allocate"][kind].format(**kwd)

    def _generate_declaration_and_allocation(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> \
std::vector<int> array = std::vector<int>(n-1+1);
        """
        # ほとんどの言語ではint, float, stringは宣言したら確保もされるはず、そうでない言語だったらこれだとまずそう
        if var.dim_num() == 0:
            return self.info["declare"][var.type.value].format(name=var.name)
        else:
            kwd = self._get_format_keywords(var)
            kind = self._get_variable_kind(var)
            return self.info["declare_and_allocate"][kind].format(**kwd)

    def _input_code_for_var(self, var: Variable) -> str:
        kwd = self._get_format_keywords(var)
        kwd["name"] = self._get_var_name(var)
        return self.info["input"][var.type.value].format(**kwd)

    def _get_var_name(self, var: Variable):
        name = var.name

        if var.dim_num() == 0:
            return name
        if var.dim_num() == 1:
            return self.info["access"]["seq"].format(
                name=name,
                index=self.info["index"]["i"],
            )
        if var.dim_num() == 2:
            return self.info["access"]["2d_seq"].format(
                name=name,
                index_i=self.info["index"]["i"],
                index_j=self.info["index"]["j"],
            )
        if var.dim_num() == 3:
            return self.info["access"]["3d_seq"].format(
                name=name,
                index_i=self.info["index"]["i"],
                index_j=self.info["index"]["j"],
                index_k=self.info["index"]["k"],
            )

        raise NotImplementedError

    def _append(self, lines, s, indent=0):
        if s == "":
            return
        for line in s.split("\n"):
            if len(lines) > 0:
                lines.append(
                    "{indent}{line}".format(
                        indent=self._indent(indent),
                        line=line))
            else:
                lines.append(line)

    def _append_declaration_and_allocation(
            self, lines, pattern: Pattern, global_mode):
        if global_mode:
            for var in pattern.all_vars():
                self._append(lines, self._generate_allocation(var))
        else:
            for var in pattern.all_vars():
                self._append(
                    lines, self._generate_declaration_and_allocation(var))

    def _append_singular_pattern(self, lines, pattern: Pattern, global_mode):
        var = pattern.all_vars()[0]
        if not global_mode:
            if "declare_and_input" in self.info:
                kwd = self._get_format_keywords(var)
                self._append(
                    lines,
                    self.info["declare_and_input"][var.type.value].format(
                        **kwd))
                return
        self._append_declaration_and_allocation(lines, pattern, global_mode)
        self._append(lines, self._input_code_for_var(var))

    def _render_pattern(
        self,
        pattern: Pattern,
        global_mode,
    ):
        lines = []
        representative_var = (
            pattern.all_vars()[0]
        )

        if isinstance(pattern, SingularPattern):
            self._append_singular_pattern(
                lines,
                pattern,
                global_mode,
            )

        elif isinstance(pattern, ParallelPattern):
            added = False

            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                kwd = self._get_format_keywords(var)

                if global_mode:
                    op = "allocate_and_input"
                else:
                    op = (
                        "declare_and_allocate_and_input"
                    )

                if op in self.info:
                    self._append(
                        lines,
                        self.info[op]["seq"].format(
                            **kwd
                        ),
                    )
                    added = True

            if not added:
                self._append_declaration_and_allocation(
                    lines,
                    pattern,
                    global_mode,
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        False,
                    ),
                )

                for var in pattern.all_vars():
                    self._append(
                        lines,
                        self._input_code_for_var(var),
                        1,
                    )

                self._append(
                    lines,
                    self.info["loop"]["footer"].format(),
                )

        elif isinstance(
            pattern,
            TwoDimensionalPattern,
        ):
            added = False

            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                kwd = self._get_format_keywords(var)

                if global_mode:
                    op = "allocate_and_input"
                else:
                    op = (
                        "declare_and_allocate_and_input"
                    )

                if op in self.info:
                    self._append(
                        lines,
                        self.info[op]["2d_seq"].format(
                            **kwd
                        ),
                    )
                    added = True

            if not added:
                self._append_declaration_and_allocation(
                    lines,
                    pattern,
                    global_mode,
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        False,
                    ),
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        True,
                    ),
                    1,
                )

                for var in pattern.all_vars():
                    self._append(
                        lines,
                        self._input_code_for_var(var),
                        2,
                    )

                self._append(
                    lines,
                    self.info["loop"]["footer"].format(
                        loop_var=self.info["index"]["j"]
                    ),
                    1,
                )
                self._append(
                    lines,
                    self.info["loop"]["footer"].format(
                        loop_var=self.info["index"]["i"]
                    ),
                )

        elif isinstance(
            pattern,
            ThreeDimensionalPattern,
        ):
            added = False

            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                kwd = self._get_format_keywords(var)

                if global_mode:
                    op = "allocate_and_input"
                else:
                    op = (
                        "declare_and_allocate_and_input"
                    )

                if (
                    op in self.info
                    and "3d_seq" in self.info[op]
                ):
                    self._append(
                        lines,
                        self.info[op]["3d_seq"].format(
                            **kwd
                        ),
                    )
                    added = True

            if not added:
                self._append_declaration_and_allocation(
                    lines,
                    pattern,
                    global_mode,
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        False,
                    ),
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        True,
                    ),
                    1,
                )
                self._append(
                    lines,
                    self._loop_header(
                        representative_var,
                        False,
                        True,
                    ),
                    2,
                )

                for var in pattern.all_vars():
                    self._append(
                        lines,
                        self._input_code_for_var(var),
                        3,
                    )

                self._append(
                    lines,
                    self.info["loop"]["footer"].format(
                        loop_var=self.info["index"]["k"]
                    ),
                    2,
                )
                self._append(
                    lines,
                    self.info["loop"]["footer"].format(
                        loop_var=self.info["index"]["j"]
                    ),
                    1,
                )
                self._append(
                    lines,
                    self.info["loop"]["footer"].format(
                        loop_var=self.info["index"]["i"]
                    ),
                )

        else:
            raise NotImplementedError

        return lines

    def _ragged_field_keywords(
        self,
        field,
        *,
        name=None,
        length=None,
    ):
        result = {
            "name": name or field.name,
            "type": self._convert_type(
                field.type
            ),
            "default": self._default_val(
                field.type
            ),
        }

        if length is not None:
            result["length"] = length

        if "input_func" in self.info:
            result["input_func"] = (
                self._get_input_func(
                    field.type
                )
            )

        return result

    def _ragged_contract_values(
        self,
        field,
        *,
        length_j,
    ):
        pattern = (
            self._ragged_format
            .ragged_pattern
        )

        return {
            "name": field.name,
            "type_": self._convert_type(
                field.type
            ),
            "default": self._default_val(
                field.type
            ),
            "length_i": (
                pattern.row_count_var
            ),
            "length_j": length_j,
            "index_i": (
                self.info["index"]["i"]
            ),
            "index_j": (
                self.info["index"]["j"]
            ),
        }

    def _ragged_seq_access(
        self,
        field,
    ):
        return self.info["access"]["seq"].format(
            name=field.name,
            index=self.info["index"]["i"],
        )

    def _ragged_input_for_field(
        self,
        field,
        name,
    ):
        keywords = (
            self._ragged_field_keywords(
                field,
                name=name,
            )
        )

        return self.info["input"][
            field.type.value
        ].format(**keywords)

    def _ragged_prefix_formal_arg(
        self,
        field,
    ):
        keywords = (
            self._ragged_field_keywords(
                field,
                length=(
                    self._ragged_format
                    .ragged_pattern
                    .row_count_var
                ),
            )
        )

        return self.info["arg"]["seq"].format(
            **keywords
        )

    def _ragged_prefix_actual_arg(
        self,
        field,
    ):
        if (
            "actual_arg" in self.info
            and "seq" in self.info[
                "actual_arg"
            ]
        ):
            return self.info[
                "actual_arg"
            ]["seq"].format(
                name=field.name
            )

        return field.name

    def _ragged_prefix_declaration(
        self,
        field,
        *,
        global_mode,
    ):
        keywords = (
            self._ragged_field_keywords(
                field,
                length=(
                    self._ragged_format
                    .ragged_pattern
                    .row_count_var
                ),
            )
        )

        if global_mode:
            declaration = self.info[
                "declare"
            ]["seq"].format(
                **keywords
            )

            if not declaration:
                return ""

            return (
                self.info["global_prefix"]
                + declaration
            )

        return self.info[
            "declare_and_allocate"
        ]["seq"].format(
            **keywords
        )

    def _ragged_prefix_allocation(
        self,
        field,
    ):
        keywords = (
            self._ragged_field_keywords(
                field,
                length=(
                    self._ragged_format
                    .ragged_pattern
                    .row_count_var
                ),
            )
        )

        return self.info["allocate"][
            "seq"
        ].format(**keywords)

    def _render_input_lines(
        self,
        lines,
    ):
        result = ""
        prefix = self._indent(
            self.info["base_indent"]
        )
        start = True

        for line in lines:
            if not line:
                continue

            if not start:
                result += "\n"

            result += prefix + line
            start = False

        return result

    def _ragged_row_input_part(
        self,
        *,
        global_mode,
    ):
        pattern = (
            self._ragged_format
            .ragged_pattern
        )

        contract = (
            RaggedCodegenContract
            .from_mapping(self.info)
        )

        lines = []

        for field in pattern.prefix_fields:
            if global_mode:
                self._append(
                    lines,
                    self._ragged_prefix_allocation(
                        field
                    ),
                )
            else:
                self._append(
                    lines,
                    (
                        self
                        ._ragged_prefix_declaration(
                            field,
                            global_mode=False,
                        )
                    ),
                )

        values_kwargs = (
            self._ragged_contract_values(
                pattern.values_field,
                length_j="0",
            )
        )

        if global_mode:
            self._append(
                lines,
                contract.render_allocate_outer(
                    **values_kwargs
                ),
            )
        else:
            self._append(
                lines,
                (
                    contract
                    .render_declare_and_allocate_outer(
                        **values_kwargs
                    )
                ),
            )

        outer_index = self.info["index"]["i"]
        inner_index = self.info["index"]["j"]

        self._append(
            lines,
            self.info["loop"]["header"].format(
                loop_var=outer_index,
                length=pattern.row_count_var,
            ),
        )

        for field in pattern.prefix_fields:
            self._append(
                lines,
                self._ragged_input_for_field(
                    field,
                    self._ragged_seq_access(
                        field
                    ),
                ),
                1,
            )

        length_access = (
            self._ragged_seq_access(
                pattern.length_field
            )
        )

        values_kwargs = (
            self._ragged_contract_values(
                pattern.values_field,
                length_j=length_access,
            )
        )

        self._append(
            lines,
            contract.render_allocate_inner(
                **values_kwargs
            ),
            1,
        )

        self._append(
            lines,
            self.info["loop"]["header"].format(
                loop_var=inner_index,
                length=length_access,
            ),
            1,
        )

        value_access = (
            contract.render_access(
                **values_kwargs
            )
        )

        self._append(
            lines,
            self._ragged_input_for_field(
                pattern.values_field,
                value_access,
            ),
            2,
        )

        self._append(
            lines,
            self.info["loop"]["footer"].format(
                loop_var=inner_index
            ),
            1,
        )

        self._append(
            lines,
            self.info["loop"]["footer"].format(
                loop_var=outer_index
            ),
        )

        prefix_input = self._get_input_part(
            global_mode=global_mode,
            format_=(
                self._ragged_format
                .prefix_format
            ),
            include_prefix=True,
        )

        ragged_input = (
            self._render_input_lines(lines)
        )

        suffix_input = self._get_input_part(
            global_mode=global_mode,
            format_=(
                self._ragged_format
                .suffix_format
            ),
            include_prefix=False,
        )

        # _get_input_part() returns a template
        # fragment whose first line is intentionally
        # unindented. Here the suffix is appended
        # after prefix and ragged fragments, so its
        # first line is a continuation line and needs
        # the normal base indentation.
        if suffix_input:
            suffix_input = (
                self._indent(
                    self.info["base_indent"]
                )
                + suffix_input
            )

        return "\n".join(
            part
            for part in (
                prefix_input,
                ragged_input,
                suffix_input,
            )
            if part
        )

    def _ragged_formal_arguments(self):
        pattern = (
            self._ragged_format
            .ragged_pattern
        )

        arguments = [
            self._get_argument(variable)
            for variable in (
                self._ragged_format
                .prefix_format
                .all_vars()
            )
        ]

        arguments.extend(
            self._ragged_prefix_formal_arg(
                field
            )
            for field
            in pattern.prefix_fields
        )

        contract = (
            RaggedCodegenContract
            .from_mapping(self.info)
        )

        arguments.append(
            contract.render_formal_arg(
                **self._ragged_contract_values(
                    pattern.values_field,
                    length_j="0",
                )
            )
        )

        arguments.extend(
            self._get_argument(variable)
            for variable in (
                self._ragged_format
                .suffix_format
                .all_vars()
            )
        )

        return ", ".join(arguments)

    def _ragged_actual_arguments(self):
        pattern = (
            self._ragged_format
            .ragged_pattern
        )

        arguments = []

        for variable in (
            self._ragged_format
            .prefix_format
            .all_vars()
        ):
            if variable.dim_num() == 0:
                arguments.append(
                    variable.name
                )
            else:
                kind = (
                    self._get_variable_kind(
                        variable
                    )
                )

                if (
                    "actual_arg" in self.info
                    and kind in self.info[
                        "actual_arg"
                    ]
                ):
                    arguments.append(
                        self.info[
                            "actual_arg"
                        ][kind].format(
                            name=variable.name
                        )
                    )
                else:
                    arguments.append(
                        variable.name
                    )

        arguments.extend(
            self._ragged_prefix_actual_arg(
                field
            )
            for field
            in pattern.prefix_fields
        )

        contract = (
            RaggedCodegenContract
            .from_mapping(self.info)
        )

        arguments.append(
            contract.render_actual_arg(
                **self._ragged_contract_values(
                    pattern.values_field,
                    length_j="0",
                )
            )
        )

        for variable in (
            self._ragged_format
            .suffix_format
            .all_vars()
        ):
            if variable.dim_num() == 0:
                arguments.append(
                    variable.name
                )
                continue

            kind = self._get_variable_kind(
                variable
            )

            if (
                "actual_arg" in self.info
                and kind in self.info[
                    "actual_arg"
                ]
            ):
                arguments.append(
                    self.info[
                        "actual_arg"
                    ][kind].format(
                        name=variable.name
                    )
                )
            else:
                arguments.append(
                    variable.name
                )

        return ", ".join(arguments)

    def _ragged_global_declaration(self):
        lines = []

        for pattern in (
            self._ragged_format
            .prefix_format
            .sequence
        ):
            for variable in pattern.all_vars():
                self._append(
                    lines,
                    (
                        self.info["global_prefix"]
                        + self._generate_declaration(
                            variable
                        )
                    ),
                )

        ragged_pattern = (
            self._ragged_format
            .ragged_pattern
        )

        for field in (
            ragged_pattern.prefix_fields
        ):
            self._append(
                lines,
                self._ragged_prefix_declaration(
                    field,
                    global_mode=True,
                ),
            )

        contract = (
            RaggedCodegenContract
            .from_mapping(self.info)
        )

        declaration = contract.render_declare(
            **self._ragged_contract_values(
                ragged_pattern.values_field,
                length_j="0",
            )
        )

        if declaration:
            self._append(
                lines,
                (
                    self.info["global_prefix"]
                    + declaration
                ),
            )

        for suffix_pattern in (
            self._ragged_format
            .suffix_format
            .sequence
        ):
            for variable in (
                suffix_pattern.all_vars()
            ):
                self._append(
                    lines,
                    (
                        self.info["global_prefix"]
                        + self._generate_declaration(
                            variable
                        )
                    ),
                )

        return "\n".join(lines)

    def _generate_ragged_parameters(self):
        local_input = (
            self._ragged_row_input_part(
                global_mode=False
            )
        )

        return dict(
            formal_arguments=(
                self._ragged_formal_arguments()
            ),
            actual_arguments=(
                self._ragged_actual_arguments()
            ),
            input_part=local_input,
            prefix_input_part=local_input,
            case_input_part="",
            global_declaration=(
                self._ragged_global_declaration()
            ),
            global_input_part=(
                self._ragged_row_input_part(
                    global_mode=True
                )
            ),
            multi_case=False,
            case_count_var=None,
            case_loop_var=None,
            ragged_row=True,
            prediction_success=True,
        )

    def _indent(self, depth):
        return self._config.indent(depth)


def get_builtin_code_generator_info_toml_path(lang):
    return Path(__file__).parent / "universal_generator" / \
        "{lang}.toml".format(lang=lang)


class NoPredictionResultGiven(Exception):
    pass
