from typing import Dict, Any, Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern, \
    Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from atcodertools.fmtprediction.models.index import Index


def _loop_header(var: Variable, index: Index, omit_name: bool):
    loop_var = '_' if omit_name else 'i'
    return 'for {loop_var} in 0..<{length} {{'.format(
        loop_var=loop_var,
        length=index.get_length()
    )


class SwiftCodeGenerator:

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
            return "Double"
        elif type_ == Type.int:
            return "Int"
        elif type_ == Type.str:
            return "String"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
        ctype = self._convert_type(var.type)
        for _ in range(var.dim_num()):
            ctype = '[{}]'.format(ctype)
        return ctype

    def _actual_arguments(self) -> str:
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([v.name for v in self._format.all_vars()])

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "_ N:Int, _ K:Int, _ a:[Int]"
        """
        return ", ".join([
            "_ {name}:{decl_type}".format(
                decl_type=self._get_declaration_type(v),
                name=v.name)
            for v in self._format.all_vars()
        ])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> var array = [Int]()
        """
        return 'var {name} = {decl_type}()'.format(name=var.name, decl_type=self._get_declaration_type(var))

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        ctype = self._convert_type(var.type)
        getnext = 'read{ctype}()'.format(ctype=ctype)
        if var.dim_num() == 0:
            return 'let {name} = {getnext}'.format(name=name, getnext=getnext)
        else:
            return '{name}.append({getnext})'.format(name=name, getnext=getnext)

    @staticmethod
    def _get_var_name(var: Variable):
        name = var.name
        if var.dim_num() >= 2:
            name += "[i]"
        return name

    def _two_dimension_header(self, var: Variable) -> str:
        name = var.name
        ctype = self._convert_type(var.type)
        return '{name}.append([{ctype}]())'.format(name=name, ctype=ctype)

    def _render_pattern(self, pattern: Pattern):
        lines = []

        if not isinstance(pattern, SingularPattern):
            for var in pattern.all_vars():
                lines.append(self._generate_declaration(var))

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.append(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, representative_var.first_index, True))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(1),
                                                     line=self._input_code_for_var(var)))
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, representative_var.first_index, False))
            lines.append("{indent}{line}".format(indent=self._indent(1),
                                                 line=self._two_dimension_header(representative_var)))
            lines.append("{indent}{line}".format(indent=self._indent(1),
                                                 line=_loop_header(representative_var, representative_var.second_index, True)))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(2),
                                                     line=self._input_code_for_var(var)))
            lines.append("{indent}}}".format(indent=self._indent(1)))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass


def main(args: CodeGenArgs) -> str:
    code_parameters = SwiftCodeGenerator(
        args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
