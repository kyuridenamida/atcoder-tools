from atcodertools.models.predictor.index import Index
from atcodertools.models.predictor.type import Type


class Variable:

    """
        This model is basically AnalyzedVariable + type information
    """

    def __init__(self,
                 var_name: str,
                 first_index: Index,
                 second_index: Index,
                 type_: Type):
        self.var_name = var_name
        self.first_index = first_index
        self.second_index = second_index
        self.type = type_

    def dim_num(self):
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0

    def get_first_index(self):
        return self.first_index

    def get_second_index(self):
        return self.second_index

    def get_name(self):
        return self.var_name

