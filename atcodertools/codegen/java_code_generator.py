from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.models.predictor.variable import Variable


class JavaCodeGenerator(CppCodeGenerator):

    def _convert_type(self, py_type: type) -> str:
        if py_type == float:
            return "double"
        elif py_type == int:
            return "long"
        elif py_type == str:
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

    def _generate_declaration(self, var: Variable):
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            constructor = " = new {type}[(int)({size})]".format(
                type=self._convert_type(var.type),
                size=var.get_first_index().get_length()
            )
        elif var.dim_num() == 2:
            constructor = " = new {type}[int({row_size})][int({col_size})]".format(
                type=self._convert_type(var.type),
                row_size=var.get_first_index().get_length(),
                col_size=var.get_second_index().get_length()
            )
        else:
            raise NotImplementedError

        line = "{decl_type} {name}{constructor};".format(
            name=var.get_name(),
            decl_type=self._get_declaration_type(var),
            constructor=constructor
        )
        return line

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        if var.type == float:
            return '{name} = sc.nextDouble();'.format(name=name)
        elif var.type == int:
            return '{name} = sc.nextLong();'.format(name=name)
        elif var.type == str:
            return '{name} = sc.next();'.format(name=name)
        else:
            raise NotImplementedError

    def _indent(self, depth):
        return "    " * (depth + 1)
