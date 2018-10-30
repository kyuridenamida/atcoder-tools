from core.Calculator import CalcNode


class Index:
    def __init__(self):
        self.min_index = None
        self.max_index = None


    def update(self, new_value: str):
        self._update_min(new_value)
        self._update_max(new_value)

    def get_zero_based_index(self):
        res = Index()
        res.min_index = CalcNode("0")
        res.max_index = CalcNode("{max_index}-({min_index})".format(max_index=self.max_index, min_index=self.min_index))
        return res

    def _update_min(self, new_value: str):
        if not new_value.isdecimal():
            # consider variable is not always could not be minimal.
            return
        if (self.min_index is None) or (self.min_index.evaluate() > CalcNode(new_value).evaluate()):
            self.min_index = CalcNode(new_value)

    def _update_max(self, new_value: str):
        if not new_value.isdecimal():
            self.max_index = CalcNode(new_value)

        if (self.max_index is None) or (
                len(self.max_index.get_all_variables()) == 0 and self.max_index.evaluate() < CalcNode(new_value).evaluate()
        ):
            self.max_index = CalcNode(new_value)