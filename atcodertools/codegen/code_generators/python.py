import re
from typing import Any, Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import (
    Format,
    ParallelPattern,
    Pattern,
    SingularPattern,
    TwoDimensionalPattern,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


def _loop_header(var: Variable, for_second_index: bool) -> str:
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"

    assert index is not None

    return f"for {loop_var} in range({_insert_space_around_operators(index.get_length())}):"


def _insert_space_around_operators(code: object) -> str:
    code = str(code)
    precode = code
    pattern = r"([0-9a-zA-Z_])([+\-\*/])([0-9a-zA-Z_])"
    code = re.sub(pattern, r"\1 \2 \3", code)
    while precode != code:
        precode = code
        code = re.sub(pattern, r"\1 \2 \3", code)
    return code


class Python3CodeGenerator:
    def __init__(self, format_: Optional[Format[Variable]], config: CodeStyleConfig) -> None:
        self._format = format_
        self._config = config

    def generate_parameters(self) -> dict[str, Any]:
        if self._format is None:
            return dict(prediction_success=False)

        return dict(
            formal_arguments=self._formal_arguments(),
            actual_arguments=self._actual_arguments(),
            input_part=self._input_part(),
            prediction_success=True,
        )

    def _input_part(self) -> str:
        assert self._format is not None
        lines = []
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern)
        return f"\n{self._indent(1)}".join(lines)

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "float"
        elif type_ == Type.int:
            return "int"
        elif type_ == Type.str:
            return "str"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable) -> str:
        ctype = self._convert_type(var.type)
        for _ in range(var.dim_num()):
            ctype = f"List[{ctype}]"
        if var.dim_num():
            ctype = f'"{ctype}"'
        return ctype

    def _actual_arguments(self) -> str:
        assert self._format is not None
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([v.name for v in self._format.all_vars()])

    def _formal_arguments(self) -> str:
        assert self._format is not None
        """
            :return the string form of formal arguments e.g. "N: int, K: int, a: List[int]"
        """
        return ", ".join([f"{v.name}: {self._get_declaration_type(v)}" for v in self._format.all_vars()])

    def _generate_declaration(self, var: Variable) -> str:
        """
        :return: Create declaration part E.g. array[1..n] -> array = [int()] * (n-1+1)  # type: List[int]
        """
        if var.dim_num() == 0:
            dims = []
        elif var.dim_num() == 1:
            assert var.first_index is not None
            dims = [var.first_index.get_length()]
        elif var.dim_num() == 2:
            assert var.first_index is not None and var.second_index is not None
            dims = [var.first_index.get_length(), var.second_index.get_length()]
        else:
            raise NotImplementedError

        ctype = self._convert_type(var.type)
        if len(dims) == 0:
            ctor = f"{ctype}()"
        elif len(dims) == 1:
            ctor = f"[{ctype}()] * ({_insert_space_around_operators(dims[0])})"
        else:
            ctor = f"[{ctype}()] * ({_insert_space_around_operators(dims[0])})"
            for dim in dims[-2::-1]:
                ctor = f"[{ctor} for _ in range({_insert_space_around_operators(dim)})]"

        line = f"{var.name} = {ctor}  # type: {self._get_declaration_type(var)}"
        return line

    def _input_code_for_token(self, type_: Type) -> str:
        if type_ == Type.float:
            return "float(next(tokens))"
        elif type_ == Type.int:
            return "int(next(tokens))"
        elif type_ == Type.str:
            return "next(tokens)"
        else:
            raise NotImplementedError

    def _input_code_for_single_pattern(self, pattern: Pattern[Variable]) -> str:
        assert len(pattern.all_vars()) == 1
        var = pattern.all_vars()[0]

        if isinstance(pattern, SingularPattern):
            input_ = self._input_code_for_token(var.type)

        elif isinstance(pattern, ParallelPattern):
            assert var.first_index is not None
            input_ = f"[{self._input_code_for_token(var.type)} for _ in range({_insert_space_around_operators(var.first_index.get_length())})]"

        elif isinstance(pattern, TwoDimensionalPattern):
            assert var.first_index is not None and var.second_index is not None
            input_ = f"[[{self._input_code_for_token(var.type)} for _ in range({_insert_space_around_operators(var.second_index.get_length())})] for _ in range({_insert_space_around_operators(var.first_index.get_length())})]"

        else:
            raise NotImplementedError

        return f"{var.name} = {input_}  # type: {self._get_declaration_type(var)}"

    @staticmethod
    def _get_var_name(var: Variable) -> str:
        name = var.name
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    def _input_code_for_non_single_pattern(self, pattern: Pattern[Variable]) -> list[str]:
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(var))
        representative_var = pattern.all_vars()[0]

        if isinstance(pattern, SingularPattern):
            raise AssertionError

        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append(f"{self._indent(1)}{self._get_var_name(var)} = {self._input_code_for_token(var.type)}")

        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(f"{self._indent(1)}{_loop_header(representative_var, True)}")
            for var in pattern.all_vars():
                lines.append(f"{self._indent(2)}{self._get_var_name(var)} = {self._input_code_for_token(var.type)}")

        else:
            raise NotImplementedError
        return lines

    def _render_pattern(self, pattern: Pattern[Variable]) -> list[str]:
        if len(pattern.all_vars()) == 1:
            return [self._input_code_for_single_pattern(pattern)]
        else:
            return self._input_code_for_non_single_pattern(pattern)

    def _indent(self, depth: int) -> str:
        return self._config.indent(depth)


def main(args: CodeGenArgs) -> str:
    code_parameters = Python3CodeGenerator(args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters,
    )
