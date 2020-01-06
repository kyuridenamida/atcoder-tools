from typing import Dict, Any, Optional

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern, \
    Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from atcodertools.codegen.code_generators.universal_generator.nim import CodeGeneratorInfo


class CodeGenerator():

    def __init__(self,
                 format_: Optional[Format[Variable]],
                 config: CodeStyleConfig, 
                 info: CodeGeneratorInfo):
        super(CodeGenerator, self).__init__()
        self._format = format_
        self._config = config
        self.info = info

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
            return self.info.type_float
        elif type_ == Type.int:
            return self.info.type_int
        elif type_ == Type.str:
            return self.info.type_string
        else:
            raise NotImplementedError

    def _default_val(self, type_: Type) -> str:
        if type_ == Type.float:
            return self.info.default_float
        elif type_ == Type.int:
            return self.info.default_int
        elif type_ == Type.str:
            return self.info.default_string
        else:
            raise NotImplementedError

    def _get_argument(self, var: Variable):
        if var.dim_num() == 0:
            if var.type == Type.float:
                return self.info.arg_float.format(name=var.name)
            elif var.type == Type.int:
                return self.info.arg_int.format(name=var.name)
            elif var.type == Type.str:
                return self.info.arg_string.format(name=var.name)
            else:
                raise NotImplementedError
        elif var.dim_num() == 1:
            return self.info.arg_seq.format(name=var.name, type=self._convert_type(var.type))
        elif var.dim_num() == 2:
            return self.info.arg_2d_seq.format(name=var.name, type=self._convert_type(var.type))

    def _actual_arguments(self) -> str:
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([
            v.name if v.dim_num() == 0 else '{}'.format(v.name)
            for v in self._format.all_vars()])

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "int N, int K, std::vector<int> a"
        """
        return ", ".join([self._get_argument(v) for v in self._format.all_vars()])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            if var.type == Type.int:
                return self.info.declare_int.format(name=var.name)
            elif var.type == Type.float:
                return self.info.declare_float.format(name=var.name)
            elif var.type == Type.str:
                return self.info.declare_string.format(name=var.name)
            else:
                raise NotImplementedError
        elif var.dim_num() == 1:
            return self.info.declare_seq.format(name=var.name, 
                                                type=self._convert_type(var.type), 
                                                length=var.first_index.get_length())
        elif var.dim_num() == 2:
            return self.info.declare_2d_seq.format(name=var.name, 
                                                   type=self._convert_type(var.type), 
                                                   length_i=var.first_index.get_length(), 
                                                   length_j=var.second_index.get_length())

    def _generate_allocation(self, var: Variable):
        """
        :return: Create allocation part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            return ""
        elif var.dim_num() == 1:
            return self.info.allocate_seq.format(name=var.name, 
                                                 length=var.first_index.get_length(),
                                                 default=self._default_val(var.type))
        elif var.dim_num() == 2:
            return self.info.allocate_2d_seq.format(name=var.name, 
                                                    type=self._convert_type(var.type),
                                                    length_i=var.first_index.get_length(),
                                                    length_j=var.second_index.get_length(),
                                                    default=self._default_val(var.type))
        else:
            raise NotImplementedError

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        if var.type == Type.float:
            return self.info.input_float.format(name=name)
        elif var.type == Type.int:
            return self.info.input_int.format(name=name)
        elif var.type == Type.str:
            return self.info.input_string.format(name=name)
        else:
            raise NotImplementedError

    def _input_code(self, var: Variable) -> str:
        if var.dim_num() == 0:
            return self._input_code_for_var(var)
        elif var.dim_num() == 1:
            return self.info.input_seq.format(length=var.first_index.get_length(),
                                              input=self._input_code_for_var(var))
        elif var.dim_num() == 2:
            return self.info.input_2d_seq.format(length_i=var.first_index.get_length(),
                                                 length_j=var.second_index.get_length(),
                                                 input=self._input_code_for_var(var))


    @staticmethod
    def _get_var_name(var: Variable):
        name = var.name
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    def append(self, lines, s, indent=0):
        if s == "":
            return
        for line in s.split("\n"):
            lines.append("{indent}{line}".format(indent=self._indent(indent),
                                                 line=line))

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            self.append(lines, self._generate_declaration(var))
            self.append(lines, self._generate_allocation(var))

        representative_var = pattern.all_vars()[0]
        self.append(lines, self._input_code(representative_var))
        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass

