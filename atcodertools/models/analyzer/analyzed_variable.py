from atcodertools.models.analyzer.index import Index


class AnalyzedVariable:

    """
        The model to have a variable's index information with up to 2 indices.
    """

    var_name = None
    first_index = None
    second_index = None

    def __init__(self, var_name, dim_num):
        self.var_name = var_name
        if dim_num >= 2:
            self.second_index = Index()
        if dim_num >= 1:
            self.first_index = Index()

    def dim_num(self):
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0
