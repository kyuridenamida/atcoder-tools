from typing import Dict, Any, Optional
import re

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern, \
    Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
# TODO why NIM?


class CodeGenerator():

    def __init__(self,
                 format_: Optional[Format[Variable]],
                 config: CodeStyleConfig,
                 info):
        super(CodeGenerator, self).__init__()
        self._format = format_
        self._config = config
        self.info = info

    def _get_length(self, index) -> str:
        return self._insert_space_around_operators(index.get_length())

    def _loop_header(self, var: Variable, for_second_index: bool):
        if for_second_index:
            index = var.second_index
            loop_var = "j"
        else:
            index = var.first_index
            loop_var = "i"

        return self.info.loop_header.format(
            loop_var=loop_var,
            length=self._get_length(index)
        )

    def _insert_space_around_operators(self, code):
        if not self.info.insert_space_around_operators:
            return code
        code = str(code)
        precode = code
        pattern = r"([0-9a-zA-Z_])([+\-\*/])([0-9a-zA-Z_])"
        code = re.sub(pattern, r"\1 \2 \3", code)
        while precode != code:
            precode = code
            code = re.sub(pattern, r"\1 \2 \3", code)
        return code

    def _global_declaration(self) -> str:
        lines = []
        for pattern in self._format.sequence:
            for var in pattern.all_vars():
                self._append(
                    lines, self.info.global_prefix + self._generate_declaration(var))
        return "\n".join(lines)

    def generate_parameters(self) -> Dict[str, Any]:
        if self._format is None:
            return dict(prediction_success=False)

        return dict(formal_arguments=self._formal_arguments(),
                    actual_arguments=self._actual_arguments(),
                    input_part=self._input_part(global_mode=False),
                    global_declaration=self._global_declaration(),
                    global_input_part=self._input_part(global_mode=True),
                    prediction_success=True)

    def _input_part(self, global_mode):
        lines = []
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern, global_mode)
        return "\n{indent}".format(indent=self._indent(self.info.base_indent)).join(lines)

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
        ret = []
        for v in self._format.all_vars():
            if v.dim_num() == 0:
                ret.append(v.name)
            elif v.dim_num() == 1:
                if hasattr(self.info, "actual_argument_1d"):
                    ret.append(
                        self.info.actual_argument_1d.format(name=v.name))
                else:
                    ret.append(v.name)
            elif v.dim_num() == 2:
                if hasattr(self.info, "actual_argument_2d"):
                    ret.append(
                        self.info.actual_argument_2d.format(name=v.name))
                else:
                    ret.append(v.name)
        return ", ".join(ret)

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
                                                type=self._convert_type(
                                                    var.type),
                                                length=self._get_length(
                                                    var.first_index))
        elif var.dim_num() == 2:
            return self.info.declare_2d_seq.format(name=var.name,
                                                   type=self._convert_type(
                                                       var.type),
                                                   length_i=self._get_length(
                                                       var.first_index),
                                                   length_j=self._get_length(
                                                       var.second_index))

    def _generate_allocation(self, var: Variable):
        """
        :return: Create allocation part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            return ""
        elif var.dim_num() == 1:
            return self.info.allocate_seq.format(name=var.name,
                                                 length=self._get_length(
                                                     var.first_index),
                                                 default=self._default_val(
                                                     var.type),
                                                 type=self._convert_type(
                                                     var.type))
        elif var.dim_num() == 2:
            return self.info.allocate_2d_seq.format(name=var.name,
                                                    type=self._convert_type(
                                                        var.type),
                                                    length_i=self._get_length(
                                                        var.first_index),
                                                    length_j=self._get_length(
                                                        var.second_index),
                                                    default=self._default_val(
                                                        var.type))
        else:
            raise NotImplementedError

    def _generate_declaration_and_allocation(self, var: Variable):
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
            return self.info.declare_and_allocate_seq.format(name=var.name,
                                                             type=self._convert_type(
                                                                 var.type),
                                                             length=self._get_length(
                                                                 var.first_index),
                                                             default=self._default_val(
                                                                 var.type))
        elif var.dim_num() == 2:
            return self.info.declare_and_allocate_2d_seq.format(name=var.name,
                                                                type=self._convert_type(
                                                                    var.type),
                                                                length_i=self._get_length(
                                                                    var.first_index),
                                                                length_j=self._get_length(
                                                                    var.second_index),
                                                                default=self._default_val(
                                                                    var.type))

    def _get_input_func(self, type: Type) -> str:
        if type == Type.float:
            return self.info.input_func_float
        elif type == Type.int:
            return self.info.input_func_int
        elif type == Type.str:
            return self.info.input_func_string

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

#    def _input_code(self, var: Variable) -> str:
#        if var.dim_num() == 0:
#            return self._input_code_for_var(var)
#        elif var.dim_num() == 1:
#            return self.info.input_seq.format(length=self._get_length(var.first_index),
#                                              input=self._input_code_for_var(var))
#        elif var.dim_num() == 2:
#            return self.info.input_2d_seq.format(length_i=self._get_length(var.first_index),
#                                                 length_j=self._get_length(var.second_index),
#                                                 input=self._input_code_for_var(var))

    def _get_var_name(self, var: Variable):
        name = var.name
        if var.dim_num() == 0:
            return name
        elif var.dim_num() == 1:
            return self.info.access_1d.format(name=name)
        elif var.dim_num() == 2:
            return self.info.access_2d.format(name=name)
        else:
            raise NotImplementedError

    def _append(self, lines, s, indent=0):
        if s == "":
            return
        for line in s.split("\n"):
            lines.append("{indent}{line}".format(indent=self._indent(indent),
                                                 line=line))

    def _append_declaration_and_allocation(self, lines, pattern: Pattern, global_mode):
        if global_mode:
            for var in pattern.all_vars():
                self._append(lines, self._generate_allocation(var))
        else:
            for var in pattern.all_vars():
                self._append(
                    lines, self._generate_declaration_and_allocation(var))

    def _append_singular_pattern(self, lines, pattern: Pattern, global_mode):
        var = pattern.all_vars()[0]
        if not global_mode:
            if var.type == Type.int:
                if hasattr(self.info, "declare_and_input_int"):
                    self._append(
                        lines, self.info.declare_and_input_int.format(name=var.name))
                    return
            elif var.type == Type.float:
                if hasattr(self.info, "declare_and_input_float"):
                    self._append(
                        lines, self.info.declare_and_input_float.format(name=var.name))
                    return
            elif var.type == Type.str:
                if hasattr(self.info, "declare_and_input_string"):
                    self._append(
                        lines, self.info.declare_and_input_string.format(name=var.name))
                    return
            else:
                raise NotImplementedError
        self._append_declaration_and_allocation(lines, pattern, global_mode)
        self._append(lines, self._input_code_for_var(var))

    def _render_pattern(self, pattern: Pattern, global_mode):
        lines = []

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            self._append_singular_pattern(lines, pattern, global_mode)
        elif isinstance(pattern, ParallelPattern):
            added = False
            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                if global_mode:
                    if hasattr(self.info, "allocate_and_input_seq"):
                        self._append(lines, self.info.allocate_and_input_seq.
                                     format(input_func=self._get_input_func(var.type),
                                            length=self._get_length(
                                                var.first_index),
                                            name=var.name))
                        added = True
                else:
                    if hasattr(self.info, "declare_and_allocate_and_input_seq"):
                        self._append(lines, self.info.declare_and_allocate_and_input_seq.
                                     format(input_func=self._get_input_func(var.type),
                                            length=self._get_length(
                                                var.first_index),
                                            name=var.name,
                                            type=self._convert_type(var.type)))

                        added = True
            if not added:
                self._append_declaration_and_allocation(
                    lines, pattern, global_mode)
                self._append(lines, self._loop_header(
                    representative_var, False))
                for var in pattern.all_vars():
                    self._append(lines, self._input_code_for_var(var), 1)
                self._append(lines, self.info.loop_footer)
        elif isinstance(pattern, TwoDimensionalPattern):
            added = False
            if len(pattern.all_vars()) == 1:
                var = pattern.all_vars()[0]
                if global_mode:
                    if hasattr(self.info, "allocate_and_input_2d_seq"):
                        self._append(lines, self.info.allocate_and_input_2d_seq.
                                     format(input_func=self._get_input_func(var.type),
                                            length_i=self._get_length(
                                                var.first_index),
                                            length_j=self._get_length(
                                                var.second_index),
                                            name=var.name))
                        added = True
                else:
                    if hasattr(self.info, "declare_and_allocate_and_input_2d_seq"):
                        self._append(lines, self.info.declare_and_allocate_and_input_2d_seq.
                                     format(input_func=self._get_input_func(var.type),
                                            length_i=self._get_length(
                                                var.first_index),
                                            length_j=self._get_length(
                                                var.second_index),
                                            name=var.name,
                                            type=self._convert_type(var.type)))
                        added = True
            if not added:
                self._append_declaration_and_allocation(
                    lines, pattern, global_mode)
                self._append(
                    lines, self._loop_header(representative_var, False))
                self._append(
                    lines, self._loop_header(representative_var, True), 1)
                for var in pattern.all_vars():
                    self._append(lines, self._input_code_for_var(var), 2)
                self._append(lines, self.info.loop_footer, 1)
                self._append(lines, self.info.loop_footer)
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass
