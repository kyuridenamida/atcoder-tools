from atcodertools.codegen.code_generators.cpp import CppCodeGenerator
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import ParallelPattern, Pattern, SingularPattern, TwoDimensionalPattern
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable

# RustCodeGenerator uses part of CppCodeGenerator just for less code clone.


def _loop_header(var: Variable, for_second_index: bool) -> str:
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"

    assert index is not None

    return f"for {loop_var} in 0..({index.get_length()}) as usize {{"


class RustCodeGenerator(CppCodeGenerator):
    def _input_part(self) -> str:
        assert self._format is not None
        lines = ["let con = read_string();", "let mut scanner = Scanner::new(&con);"]
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern)
        return f"\n{self._indent(1)}".join(lines)

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "f64"
        elif type_ == Type.int:
            return "i64"
        elif type_ == Type.str:
            return "String"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable) -> str:
        if var.dim_num() == 0:
            template = "{type}"
        elif var.dim_num() == 1:
            template = "Vec<{type}>"
        elif var.dim_num() == 2:
            template = "Vec<Vec<{type}>>"
        else:
            raise NotImplementedError
        return template.format(type=self._convert_type(var.type))

    def _actual_arguments(self) -> str:
        assert self._format is not None
        return ", ".join([v.name for v in self._format.all_vars()])

    def _formal_arguments(self) -> str:
        assert self._format is not None
        """
            :return the string form of formal arguments e.g. "N: i64, K: i64, a: Vec<i64>"
        """
        return ", ".join([f"{v.name}: {self._get_declaration_type(v)}" for v in self._format.all_vars()])

    def _generate_declaration(self, var: Variable) -> str:
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            if var.type == Type.str:
                assert var.first_index is not None
                constructor = f" = vec![String::new(); ({var.first_index.get_length()}) as usize]"
            else:
                assert var.first_index is not None
                constructor = f" = vec![0{self._convert_type(var.type)}; ({var.first_index.get_length()}) as usize]"
        elif var.dim_num() == 2:
            if var.type == Type.str:
                assert var.first_index is not None and var.second_index is not None
                constructor = f" = vec![vec![String::new(); ({var.second_index.get_length()}) as usize]; ({var.first_index.get_length()}) as usize]"
            else:
                assert var.first_index is not None and var.second_index is not None
                constructor = f" = vec![vec![0{self._convert_type(var.type)}; ({var.second_index.get_length()}) as usize]; ({var.first_index.get_length()}) as usize]"
        else:
            raise NotImplementedError

        line = f"let mut {var.name}: {self._get_declaration_type(var)}{constructor};"
        return line

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        return f"{name} = scanner.next();"

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


def main(args: CodeGenArgs) -> str:
    code_parameters = RustCodeGenerator(args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters,
    )
