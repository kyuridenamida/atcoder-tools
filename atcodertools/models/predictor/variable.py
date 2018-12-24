from atcodertools.models.analyzer.analyzed_variable import AnalyzedVariable


class Variable:

    """
        This model is basically AnalyzedVariable + type information
    """

    def __init__(self, var: AnalyzedVariable, type_: type):
        self.var = var
        self.type = type_

    def dim_num(self):
        return self.var.dim_num()

    def get_first_index(self):
        return self.var.first_index

    def get_second_index(self):
        return self.var.second_index

    def get_name(self):
        return self.var.var_name
