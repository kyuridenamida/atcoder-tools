from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.code_generators.cpp import CppCodeGenerator
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable


# JavaCodeGenerator uses part of CppCodeGenerator just for less code clone.

class JavaCodeGenerator(CppCodeGenerator):

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "double"
        elif type_ == Type.int:
            return "long"
        elif type_ == Type.str:
            return "String"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
        if var.dim_num() == 0:
            template = "{type}"
        elif var.dim_num() == 1:
            template = "{type}[]"
        elif var.dim_num() == 2:
            template = "{type}[][]"
        else:
            raise NotImplementedError
        return template.format(type=self._convert_type(var.type))

    def _actual_arguments(self) -> str:
        return ", ".join([v.name for v in self._format.all_vars()])

    def _generate_declaration(self, var: Variable):
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            constructor = " = new {type}[(int)({size})]".format(
                type=self._convert_type(var.type),
                size=var.first_index.get_length()
            )
        elif var.dim_num() == 2:
            constructor = " = new {type}[(int)({row_size})][(int)({col_size})]".format(
                type=self._convert_type(var.type),
                row_size=var.first_index.get_length(),
                col_size=var.second_index.get_length()
            )
        else:
            raise NotImplementedError

        line = "{decl_type} {name}{constructor};".format(
            name=var.name,
            decl_type=self._get_declaration_type(var),
            constructor=constructor
        )
        return line

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        if var.type == Type.float:
            return '{name} = sc.nextDouble();'.format(name=name)
        elif var.type == Type.int:
            return '{name} = sc.nextLong();'.format(name=name)
        elif var.type == Type.str:
            return '{name} = sc.next();'.format(name=name)
        else:
            raise NotImplementedError

    def _indent(self, depth):
        return "    " * (depth + 1)


def main(args: CodeGenArgs) -> str:
    code_parameters = JavaCodeGenerator(
        args.format, args.config).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
