from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.code_generators.cpp import CppCodeGenerator
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


# RustCodeGenerator uses part of CppCodeGenerator just for less code clone.


def _loop_header(var: Variable, for_second_index: bool):
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"

    return "for {loop_var} in 0..({length}) as usize {{".format(
        loop_var=loop_var,
        length=index.get_length()
    )


class RustCodeGenerator(CppCodeGenerator):

    def _input_part(self):
        lines = ["let con = read_string();",
                 "let mut scanner = Scanner::new(&con);"]
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern)
        return "\n{indent}".format(indent=self._indent(1)).join(lines)

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "f64"
        elif type_ == Type.int:
            return "i64"
        elif type_ == Type.str:
            return "String"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
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
        return ", ".join([v.name for v in self._format.all_vars()])

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "N: i64, K: i64, a: Vec<i64>"
        """
        return ", ".join([
            "{name}: {decl_type}".format(
                decl_type=self._get_declaration_type(v),
                name=v.name)
            for v in self._format.all_vars()
        ])

    def _generate_declaration(self, var: Variable):
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            if var.type == Type.str:
                constructor = " = vec![String::new(); ({size}) as usize]".format(
                    size=var.first_index.get_length()
                )
            else:
                constructor = " = vec![0{type}; ({size}) as usize]".format(
                    type=self._convert_type(var.type),
                    size=var.first_index.get_length()
                )
        elif var.dim_num() == 2:
            if var.type == Type.str:
                constructor = " = vec![vec![String::new(); ({col_size}) as usize]; ({row_size}) as usize]".format(
                    row_size=var.first_index.get_length(),
                    col_size=var.second_index.get_length()
                )
            else:
                constructor = " = vec![vec![0{type}; ({col_size}) as usize]; ({row_size}) as usize]".format(
                    type=self._convert_type(var.type),
                    row_size=var.first_index.get_length(),
                    col_size=var.second_index.get_length()
                )
        else:
            raise NotImplementedError

        line = "let mut {name}: {decl_type}{constructor};".format(
            name=var.name,
            decl_type=self._get_declaration_type(var),
            constructor=constructor
        )
        return line

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        return '{name} = scanner.next();'.format(name=name)

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(var))

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.append(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(1),
                                                     line=self._input_code_for_var(var)))
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(
                "{indent}{line}".format(indent=self._indent(1), line=_loop_header(representative_var, True)))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(2),
                                                     line=self._input_code_for_var(var)))
            lines.append("{indent}}}".format(indent=self._indent(1)))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines


def main(args: CodeGenArgs) -> str:
    code_parameters = RustCodeGenerator(
        args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
