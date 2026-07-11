# -*- coding: utf-8 -*-
from typing import Dict, Any, Optional
import re

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.fmtprediction.models.format import (
    Format,
    ParallelPattern,
    Pattern,
    RepeatedCaseFormat,
    SingularPattern,
    TwoDimensionalPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from pathlib import Path
import toml


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
        self.info = toml.load(path)

        if "index" not in self.info:
            self.info["index"] = {
                "i": "i",
                "j": "j",
            }

        self._prefix_format = format_
        self._solve_format = format_
        self._case_count_var = None
        self._case_loop_var = None

        if isinstance(format_, RepeatedCaseFormat):
            self._prefix_format = format_.prefix_format
            self._solve_format = format_.case_format
            self._case_count_var = format_.case_count_var
            self._case_loop_var = (
                self._choose_case_loop_var()
            )

    def _get_length(self, index) -> str:
        return self._insert_space_around_operators(str(index.get_length()))

    def _loop_header(self, var: Variable, for_second_index: bool):
        if for_second_index:
            index = var.second_index
            loop_var = self.info["index"]["j"]
        else:
            index = var.first_index
            loop_var = self.info["index"]["i"]

        return self.info["loop"]["header"].format(
            loop_var=loop_var,
            length=self._get_length(index)
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

        if "solve_function" in self.info:
            combined_input_part = (
                self._input_part_with_solve_function()
            )

            parameters[
                "input_part_with_solve_function"
            ] = combined_input_part

            # Rust places the generated input loop one level deeper,
            # inside its stack-sized worker thread. The first line gets
            # indentation from the template; continuation lines need one
            # additional configured indentation level.
            parameters[
                "input_part_with_solve_function_nested"
            ] = combined_input_part.replace(
                "\n",
                "\n" + self._indent(1),
            )
        else:
            # Preserve custom configurations which do not define a
            # solve-function call yet.
            parameters[
                "input_part_with_solve_function"
            ] = input_part

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

        if newline_after_input:
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

    def _solve_function_call(self):
        return self.info["solve_function"].format(
            actual_arguments=self._actual_arguments(),
        )

    def _input_part_with_solve_function(self):
        solve_call = self._solve_function_call()
        base_indent = self._indent(
            self.info["base_indent"]
        )

        if self._case_count_var is None:
            result = self._get_input_part(
                global_mode=False,
                format_=self._solve_format,
                include_prefix=True,
            )

            if result != "":
                result += "\n" + base_indent

            return result + solve_call

        result = self._get_input_part(
            global_mode=False,
            format_=self._prefix_format,
            include_prefix=True,
        )

        loop_header = self.info["loop"][
            "header"
        ].format(
            loop_var=self._case_loop_var,
            length=self._case_count_var,
        )

        if result != "":
            result += "\n" + base_indent

        result += loop_header

        case_input = self._get_input_part(
            global_mode=False,
            format_=self._solve_format,
            include_prefix=False,
        )

        if case_input != "":
            # _get_input_part already indents continuation lines by one
            # base indentation level. Prefix once, then nest the entire
            # block by one additional loop level.
            case_block = base_indent + case_input
            nested_case_block = "\n".join(
                self._indent(1) + line
                for line in case_block.split("\n")
            )

            result += "\n" + nested_case_block

        result += (
            "\n"
            + base_indent
            + self._indent(1)
            + solve_call
        )

        loop_footer = self.info["loop"][
            "footer"
        ].format(
            loop_var=self._case_loop_var,
        )

        if loop_footer != "":
            result += (
                "\n"
                + base_indent
                + loop_footer
            )

        return result

    def _convert_type(self, type_: Type) -> str:
        return self.info["type"][type_.value]

    def _default_val(self, type_: Type) -> str:
        return self.info["default"][type_.value]

    def _get_input_func(self, type_: Type) -> str:
        return self.info["input_func"][type_.value]

    def _get_format_keywords(self, var: Variable) -> dict:
        result = {"name": var.name, "type": self._convert_type(
            var.type), "default": self._default_val(var.type)}
        if "input_func" in self.info:
            result["input_func"] = self._get_input_func(var.type)
        if var.dim_num() == 0:
            pass
        elif var.dim_num() == 1:
            result["length"] = self._get_length(var.first_index)
        elif var.dim_num() == 2:
            result.update({"length_i": self._get_length(
                var.first_index), "length_j": self._get_length(var.second_index)})
        else:
            raise NotImplementedError
        # TODO: index_i, index_jは含めなくていいか？
        return result

    def _get_variable_kind(self, var: Variable) -> str:
        if var.dim_num() == 0:
            return var.type.value
        elif var.dim_num() == 1:
            return "seq"
        elif var.dim_num() == 2:
            return "2d_seq"
        else:
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
        :return: Create declaration part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        kwd = self._get_format_keywords(var)
        kind = self._get_variable_kind(var)
        return self.info["declare"][kind].format(**kwd)

    def _generate_allocation(self, var: Variable):
        """
        :return: Create allocation part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:  # ほとんどの言語ではint, float, stringは宣言したら確保もされるはず、そうでない言語だったらこれだとまずそう
            return ""
        else:
            kwd = self._get_format_keywords(var)
            kind = self._get_variable_kind(var)
            return self.info["allocate"][kind].format(**kwd)

    def _generate_declaration_and_allocation(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:  # ほとんどの言語ではint, float, stringは宣言したら確保もされるはず、そうでない言語だったらこれだとまずそう
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
        elif var.dim_num() == 1:
            return self.info["access"]["seq"].format(name=name, index=self.info["index"]["i"])
        elif var.dim_num() == 2:
            return self.info["access"]["2d_seq"].format(name=name, index_i=self.info["index"]["i"], index_j=self.info["index"]["j"])
        else:
            raise NotImplementedError

    def _append(self, lines, s, indent=0):
        if s == "":
            return
        for line in s.split("\n"):
            if len(lines) > 0:
                lines.append("{indent}{line}".format(indent=self._indent(indent),
                                                     line=line))
            else:
                lines.append(line)

    def _append_declaration_and_allocation(self, lines, pattern: Pattern, global_mode):
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
                    lines, self.info["declare_and_input"][var.type.value].format(**kwd))
                return
        self._append_declaration_and_allocation(lines, pattern, global_mode)
        self._append(lines, self._input_code_for_var(var))

    def _render_pattern(self, pattern: Pattern, global_mode):
        lines = []

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            self._append_singular_pattern(lines, pattern, global_mode)
        elif isinstance(pattern, ParallelPattern):
            added = False
            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                kwd = self._get_format_keywords(var)
                if global_mode:
                    op = "allocate_and_input"
                else:
                    op = "declare_and_allocate_and_input"
                if op in self.info:
                    self._append(lines, self.info[op]["seq"].format(**kwd))
                    added = True
            if not added:
                self._append_declaration_and_allocation(
                    lines, pattern, global_mode)
                self._append(lines, self._loop_header(
                    representative_var, False))
                for var in pattern.all_vars():
                    self._append(lines, self._input_code_for_var(var), 1)
                self._append(lines, self.info["loop"]["footer"].format())
        elif isinstance(pattern, TwoDimensionalPattern):
            added = False
            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                kwd = self._get_format_keywords(var)
                if global_mode:
                    op = "allocate_and_input"
                else:
                    op = "declare_and_allocate_and_input"
                if op in self.info:
                    self._append(lines, self.info[op]["2d_seq"].format(**kwd))
                    added = True
            if not added:
                self._append_declaration_and_allocation(
                    lines, pattern, global_mode)
                self._append(
                    lines, self._loop_header(representative_var, False))
                self._append(
                    lines, self._loop_header(representative_var, True), 1)
                for var in pattern.all_vars():
                    self._append(lines, self._input_code_for_var(var), 2)
                # loop_varを指定してるのはVisual Basicなどfooterにループの変数書かなきゃいけない言語向けのつもり
                self._append(lines, self.info["loop"]["footer"].format(
                    loop_var=self.info["index"]["j"]), 1)
                self._append(lines, self.info["loop"]["footer"].format(
                    loop_var=self.info["index"]["i"]))
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


def get_builtin_code_generator_info_toml_path(lang):
    return Path(__file__).parent / "universal_generator" / "{lang}.toml".format(lang=lang)


class NoPredictionResultGiven(Exception):
    pass
