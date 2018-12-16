import os
from functools import reduce

from core.TemplateEngine import render
from core.models.analyzer import AnalyzedVariable
from core.models.analyzer.SimpleFormat import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern
from core.models.predictor.FormatPredictionResult import FormatPredictionResult
from core.models.predictor.Variable import Variable

mydir = os.path.dirname(__file__)

TAB = "    "


class CodeGenerator:
    def __init__(self, prediction_result: FormatPredictionResult):
        self.prediction_result = prediction_result

    def get_code(self):
        if self.prediction_result is None:
            return self._code_when_failed()
        return self._code_when_succeeded()

    def _code_when_succeeded(self):
        with open("{dir}/template_success.cpp".format(dir=mydir), "r") as f:
            template_success = f.read()
            return render(template_success,
                          formal_arguments=self._formal_arguments(),
                          actual_arguments=self._actual_arguments(),
                          input_part=self._input_part())

    def _code_when_failed(self):
        with open("{dir}/template_failure.cpp".format(dir=mydir), "r") as f:
            return f.read()

    def _input_part(self):
        lines = []
        for pattern in self.prediction_result.simple_format.sequence:
            lines += self._render_pattern(pattern)
        return "\n    ".join(lines)

    def _convert_type(self, py_type: type) -> str:
        if py_type == float:
            return "long double"
        elif py_type == int:
            return "long long"
        elif py_type == str:
            return "string"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
        if var.dim_num() == 0:
            template = "{type}"
        elif var.dim_num() == 1:
            template = "vector<{type}>"
        elif var.dim_num() == 2:
            template = "vector<vector<{type}>>"
        else:
            raise NotImplementedError
        return template.format(type=self._convert_type(var.type))

    def _actual_arguments(self) -> str:
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join(self.prediction_result.var_to_info.keys())

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "int N, int K, vector<int> a"
        """
        return ", ".join([
            "{decl_type} {name}".format(decl_type=self._get_declaration_type(var), name=vname)
            for vname, var in self.prediction_result.var_to_info.items()
        ])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] → vector<int> array = vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            constructor = "({size}+1)".format(size=var.get_first_index().get_zero_based_index().max_index)
        elif var.dim_num() == 2:
            constructor = "({row_size}+1,vector<{type}>({col_size}+1))".format(
                type=self._convert_type(var.type),
                row_size=var.get_first_index().get_zero_based_index().max_index,
                col_size=var.get_second_index().get_zero_based_index().max_index
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
        if var.type == float:
            return 'scanf("%Lf",&{name});'.format(name=var.get_name())
        elif var.type == int:
            return 'scanf("%lld",&{name});'.format(name=var.get_name())
        elif var.type == str:
            return 'cin >> {name};'.format(name=var.get_name())
        else:
            raise NotImplementedError

    def _analyzed_var_to_vinfo(self, var: AnalyzedVariable) -> Variable:
        return self.prediction_result.var_to_info[var.var_name]

    def _loop_header(self, var: Variable, for_second_index: bool):
        if for_second_index:
            index = var.get_second_index()
            loop_var = "j"
        else:
            index = var.get_first_index()
            loop_var = "i"

        return "for(int {loop_var} = {start} ; {loop_var} <= {end} ; {loop_var}++){{".format(
            loop_var=loop_var,
            start=index.get_zero_based_index().min_index,
            end=index.get_zero_based_index().max_index
        )

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(self._analyzed_var_to_vinfo(var)))

        representative_var = self._analyzed_var_to_vinfo(pattern.all_vars()[0])
        if type(pattern) == SingularPattern:
            lines.append(self._input_code_for_var(representative_var))
        elif type(pattern) == ParallelPattern:
            lines.append(self._loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append("    {line}".format(line=self._input_code_for_var(self._analyzed_var_to_vinfo(var))))
            lines.append("}")
        elif type(pattern) == TwoDimensionalPattern:
            lines.append(self._loop_header(representative_var, False))
            lines.append("    {line}".format(line=self._loop_header(representative_var, True)))
            for var in pattern.all_vars():
                lines.append("        {line}".format(line=self._input_code_for_var(self._analyzed_var_to_vinfo(var))))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines


def generate_code(prediction_result: FormatPredictionResult):
    generator = CodeGenerator
    return generator(prediction_result).get_code()
