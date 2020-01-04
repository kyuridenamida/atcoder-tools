from typing import Dict, Any, Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern, \
    Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


def _make_loop_header(loop_var: str, length: str):
    return "for {loop_var} := int64(0); {loop_var} < {length}; {loop_var}++ {{".format(
        loop_var=loop_var,
        length=length
    )


def _loop_header(var: Variable, for_second_index: bool):
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"
    return "for {loop_var} := int64(0); {loop_var} < {length}; {loop_var}++ {{".format(
        loop_var=loop_var,
        length=index.get_length()
    )


class GoCodeGenerator:

    def __init__(self,
                 format_: Optional[Format[Variable]],
                 config: CodeStyleConfig):
        self._format = format_
        self._config = config

    def generate_parameters(self) -> Dict[str, Any]:
        if self._format is None:
            return dict(prediction_success=False)

        return dict(formal_arguments=self._formal_arguments(),
                    actual_arguments=self._actual_arguments(),
                    input_part=self._input_part(),
                    prediction_success=True)

    def _input_part(self):
        lines = []
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern)
        return "\n{indent}".format(indent=self._indent(1)).join(lines)

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "float64"
        elif type_ == Type.int:
            return "int64"
        elif type_ == Type.str:
            return "string"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
        ctype = self._convert_type(var.type)
        for _ in range(var.dim_num()):
            ctype = '[]{}'.format(ctype)
        return ctype

    def _actual_arguments(self) -> str:
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([v.name for v in self._format.all_vars()])

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "N int, K int, a []int"
        """
        return ", ".join([
            "{name} {decl_type}".format(
                decl_type=self._get_declaration_type(v),
                name=v.name)
            for v in self._format.all_vars()
        ])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part as string[] E.g. array[1..n] -> ["array := make([]int, n)"]
        array[1..n][1..m] ->
        [
            "array := make([][]int, n)",
            "for i := 0; i < m; i++ {",
            "	array[i] = make([]int, m)",
            "}",
        ]
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

        lines = []

        if len(dims) == 0:
            lines.append("var {name} {decl_type}".format(name=var.name,
                                                         decl_type=self._get_declaration_type(var)))
        else:
            lines.append("{name} := make({decl_type}, {dim})".format(name=var.name,
                                                                     decl_type=self._get_declaration_type(
                                                                         var),
                                                                     dim=dims[0]))

            indexes = ""
            loop_vars = list("ijk")
            ctype = self._convert_type(var.type)
            for i, dim in enumerate(dims[1::1]):
                loop_var = loop_vars[i]
                lines.append(_make_loop_header(loop_var, dims[i]))
                indexes += "[{}]".format(loop_var)
                brackets = "[]" * (len(dims) - i - 1)
                lines.append(
                    "{indent}{name}{indexes} = make({brackets}{ctype}, {dim})".format(indent=self._indent(i + 1),
                                                                                      name=var.name,
                                                                                      indexes=indexes,
                                                                                      brackets=brackets,
                                                                                      ctype=ctype,
                                                                                      dim=dim
                                                                                      ))

            for i in reversed(range(len(dims) - 1)):
                lines.append("{indent}}}".format(indent=self._indent(i)))

        return lines

    def _input_code_for_var(self, var: Variable):
        lines = ["scanner.Scan()"]
        name = self._get_var_name(var)
        if var.type == Type.float:
            lines.append(
                '{name}, _ = strconv.ParseFloat(scanner.Text(), 64)'.format(name=name))
        elif var.type == Type.int:
            lines.append(
                '{name}, _ = strconv.ParseInt(scanner.Text(), 10, 64)'.format(name=name))
        elif var.type == Type.str:
            lines.append('{name} = scanner.Text()'.format(name=name))
        else:
            raise NotImplementedError
        return lines

    @staticmethod
    def _get_var_name(var: Variable):
        name = var.name
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            lines.extend(self._generate_declaration(var))

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.extend(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                for line in self._input_code_for_var(var):
                    lines.append("{indent}{line}".format(
                        indent=self._indent(1), line=line))
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(
                "{indent}{line}".format(indent=self._indent(1), line=_loop_header(representative_var, True)))
            for var in pattern.all_vars():
                for line in self._input_code_for_var(var):
                    lines.append("{indent}{line}".format(
                        indent=self._indent(2), line=line))
            lines.append("{indent}}}".format(indent=self._indent(1)))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        # TODO: 言語設定でタブのデフォルト設定ができるようになったら_configを使う
        # return self._config.indent(depth)
        return "\t" * 1 * depth


class NoPredictionResultGiven(Exception):
    pass


def main(args: CodeGenArgs) -> str:
    code_parameters = GoCodeGenerator(
        args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
