from typing import Dict, Any, Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import (
    Pattern,
    SingularPattern,
    ParallelPattern,
    TwoDimensionalPattern,
    Format)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


def _loop_header(var: Variable, for_second_index: bool):
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"

    return "foreach ({loop_var}; 0 .. cast(size_t) ({length})) {{".format(
        loop_var=loop_var,
        length=index.get_length())


class DlangCodeGenerator:
    def __init__(self,
                 format_: Optional[Format[Variable]],
                 config: CodeStyleConfig):
        self._format = format_
        self._config = config

    def generate_parameters(self) -> Dict[str, Any]:
        if self._format is None:
            return dict(prediction_success=False)

        return dict(
            formal_arguments=self._formal_arguments(),
            actual_arguments=self._actual_arguments(),
            input_part=self._input_part(),
            prediction_success=True)

    def _formal_arguments(self):
        """
        :return the string form of formal arguments e.g. "int N, int K, int[] a"
        """
        return ", ".join([
            "{decl_type} {name}".format(
                decl_type=self._get_declaration_type(v),
                name=v.name)
            for v in self._format.all_vars()])

    def _actual_arguments(self) -> str:
        """
        :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([v.name for v in self._format.all_vars()])

    def _input_part(self):
        lines = []
        for pattern in self._format.sequence:
            lines.extend(self._render_pattern(pattern))
            lines.append("")

        code = "auto input = stdin.byLine.map!split.joiner;\n\n"
        for line in lines:
            if line == "":
                code += "\n"
            else:
                code += "{indent}{line}\n".format(
                    indent=self._indent(1),
                    line=line)

        return code[:-1]

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(var))

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.extend(self._assignment_code(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.extend(self._assignment_code(var, indent_level=1))
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(
                "{indent}{line}".format(
                    indent=self._indent(1),
                    line=_loop_header(representative_var, True)))
            for var in pattern.all_vars():
                lines.extend(self._assignment_code(var, indent_level=2))
            lines.append("{indent}}}".format(indent=self._indent(1)))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part e.g. array[1..n] -> int[] array = new int[](n-1+1);
        """
        if var.dim_num() == 0:
            dims = []
        elif var.dim_num() == 1:
            dims = [var.first_index.get_length()]
        elif var.dim_num() == 2:
            dims = [var.first_index.get_length(),
                    var.second_index.get_length()]
        else:
            raise NotImplementedError

        decl_type = self._get_declaration_type(var)
        line = "{decl_type} {name}".format(
            name=var.name,
            decl_type=decl_type)

        if len(dims) > 0:
            ctor_args = map(lambda d: "cast(size_t) ({})".format(d), dims)
            line += ' = new {}({})'.format(decl_type, ", ".join(ctor_args))

        line += ";"

        return line

    def _assignment_code(self, var: Variable, indent_level: int = 0) -> str:
        line1 = "{indent}{varname} = input.front.to!{vartype};"
        line2 = "{indent}input.popFront;"
        indent = self._indent(indent_level)

        return [
            line1.format(
                indent=indent,
                varname=self._get_var_name(var),
                vartype=self._get_var_basetype(var)),
            line2.format(
                indent=indent)]

    @staticmethod
    def _get_var_name(var: Variable):
        name = var.name
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    @staticmethod
    def _get_var_basetype(var: Variable) -> str:
        type_ = var.type
        if type_ == Type.float:
            return "double"
        elif type_ == Type.int:
            return "long"
        elif type_ == Type.str:
            return "string"
        else:
            raise NotImplementedError

    @classmethod
    def _get_declaration_type(cls, var: Variable):
        ctype = cls._get_var_basetype(var)
        for _ in range(var.dim_num()):
            ctype += "[]"
        return ctype

    def _indent(self, depth):
        return self._config.indent(depth)


def main(args: CodeGenArgs) -> str:
    code_parameters = DlangCodeGenerator(
        args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters)
