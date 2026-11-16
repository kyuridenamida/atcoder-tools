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

    return f"for(int {loop_var} = 0 ; {loop_var} < {index.get_length()} ; {loop_var}++){{"


class CppCodeGenerator:
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
            return "long double"
        elif type_ == Type.int:
            return "long long"
        elif type_ == Type.str:
            return "std::string"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable) -> str:
        ctype = self._convert_type(var.type)
        for _ in range(var.dim_num()):
            ctype = f"std::vector<{ctype}>"
        return ctype

    def _actual_arguments(self) -> str:
        assert self._format is not None
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([v.name if v.dim_num() == 0 else f"std::move({v.name})" for v in self._format.all_vars()])

    def _formal_arguments(self) -> str:
        assert self._format is not None
        """
            :return the string form of formal arguments e.g. "int N, int K, std::vector<int> a"
        """
        return ", ".join([f"{self._get_declaration_type(v)} {v.name}" for v in self._format.all_vars()])

    def _generate_declaration(self, var: Variable) -> str:
        """
        :return: Create declaration part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
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

        if len(dims) == 0:
            ctor = ""
        elif len(dims) == 1:
            ctor = f"({dims[0]})"
        else:
            ctor = f"({dims[-1]})"
            ctype = self._convert_type(var.type)
            for dim in dims[-2::-1]:
                ctype = f"std::vector<{ctype}>"
                ctor = f"({dim}, {ctype}{ctor})"

        line = f"{self._get_declaration_type(var)} {var.name}{ctor};"
        return line

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        if var.type == Type.float:
            return f'scanf("%Lf",&{name});'
        elif var.type == Type.int:
            return f'scanf("%lld",&{name});'
        elif var.type == Type.str:
            return f"std::cin >> {name};"
        else:
            raise NotImplementedError

    @staticmethod
    def _get_var_name(var: Variable) -> str:
        name = var.name
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    def _render_pattern(self, pattern: Pattern[Variable]) -> list[str]:
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(var))

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.append(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append(f"{self._indent(1)}{self._input_code_for_var(var)}")
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(f"{self._indent(1)}{_loop_header(representative_var, True)}")
            for var in pattern.all_vars():
                lines.append(f"{self._indent(2)}{self._input_code_for_var(var)}")
            lines.append(f"{self._indent(1)}}}")
            lines.append("}")
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth: int) -> str:
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass


def main(args: CodeGenArgs) -> str:
    code_parameters = CppCodeGenerator(args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters,
    )
