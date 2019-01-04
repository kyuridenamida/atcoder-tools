from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.models.analyzer.analyzed_variable import AnalyzedVariable
from atcodertools.models.analyzer.simple_format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern
from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from atcodertools.models.predictor.format_prediction_result import FormatPredictionResult
from atcodertools.models.predictor.variable import Variable
from atcodertools.codegen.code_generator import CodeGenerator
from atcodertools.codegen.template_engine import render


def _loop_header(var: Variable, for_second_index: bool):
    if for_second_index:
        index = var.get_second_index()
        loop_var = "j"
    else:
        index = var.get_first_index()
        loop_var = "i"

    return "for(int {loop_var} = 0 ; {loop_var} < {length} ; {loop_var}++){{".format(
        loop_var=loop_var,
        length=index.get_length()
    )


class CppCodeGenerator(CodeGenerator):

    def __init__(self, template: str, config: CodeStyleConfig = CodeStyleConfig()):
        self._template = template
        self._prediction_result = None
        self._config = config

    def generate_code(self, prediction_result: FormatPredictionResult,
                      constants: ProblemConstantSet = ProblemConstantSet()):
        if prediction_result is None:
            raise NoPredictionResultGiven
        self._prediction_result = prediction_result

        return render(self._template,
                      formal_arguments=self._formal_arguments(),
                      actual_arguments=self._actual_arguments(),
                      input_part=self._input_part(),
                      mod=constants.mod,
                      yes_str=constants.yes_str,
                      no_str=constants.no_str,
                      )

    def _input_part(self):
        lines = []
        for pattern in self._prediction_result.simple_format.sequence:
            lines += self._render_pattern(pattern)
        return "\n{indent}".format(indent=self._indent(1)).join(lines)

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
        return ", ".join(self._prediction_result.var_to_info.keys())

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "int N, int K, vector<int> a"
        """
        return ", ".join([
            "{decl_type} {name}".format(
                decl_type=self._get_declaration_type(var),
                name=vname)
            for vname, var in self._prediction_result.var_to_info.items()
        ])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] → vector<int> array = vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            constructor = ""
        elif var.dim_num() == 1:
            constructor = "({size})".format(
                size=var.get_first_index().get_length())
        elif var.dim_num() == 2:
            constructor = "({row_size}, vector<{type}>({col_size}))".format(
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
            return 'scanf("%Lf",&{name});'.format(name=name)
        elif var.type == int:
            return 'scanf("%lld",&{name});'.format(name=name)
        elif var.type == str:
            return 'cin >> {name};'.format(name=name)
        else:
            raise NotImplementedError

    @staticmethod
    def _get_var_name(var: Variable):
        name = var.get_name()
        if var.dim_num() >= 1:
            name += "[i]"
        if var.dim_num() >= 2:
            name += "[j]"
        return name

    def _analyzed_var_to_vinfo(self, var: AnalyzedVariable) -> Variable:
        return self._prediction_result.var_to_info[var.var_name]

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            lines.append(self._generate_declaration(
                self._analyzed_var_to_vinfo(var)))

        representative_var = self._analyzed_var_to_vinfo(pattern.all_vars()[0])
        if isinstance(pattern, SingularPattern):
            lines.append(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(1),
                                                     line=self._input_code_for_var(self._analyzed_var_to_vinfo(var))))
            lines.append("}")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(
                "{indent}{line}".format(indent=self._indent(1), line=_loop_header(representative_var, True)))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(2),
                                                     line=self._input_code_for_var(self._analyzed_var_to_vinfo(var))))
            lines.append("{indent}}}".format(indent=self._indent(1)))
            lines.append("}")
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass
