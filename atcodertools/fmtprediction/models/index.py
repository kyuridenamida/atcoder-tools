from atcodertools.fmtprediction.models.calculator import CalcNode


class Index:

    """
        The model to store index information of a variable, which has a likely the minimal / maximal value and for each dimension.
        Up to 2 indices are now supported.

        In most cases, the minimal value is 1 and the maximal value is some variable like N.
    """

    def __init__(self):
        self.min_index = None
        self.max_index = None

    def update(self, new_value: str):
        self._update_min(new_value)
        self._update_max(new_value)

    def get_length(self):
        assert self.max_index is not None
        assert self.min_index is not None
        return CalcNode.parse(
            "{max_index}-({min_index})+1".format(
                max_index=self.max_index,
                min_index=self.min_index)
        ).simplify()

    def _update_min(self, new_value: str):
        if not new_value.isdecimal():
            # consider variable is not always could not be minimal.
            return
        if (self.min_index is None) or (self.min_index.evaluate() > CalcNode.parse(new_value).evaluate()):
            self.min_index = CalcNode.parse(new_value)

    def _update_max(self, new_value: str):
        if not new_value.isdecimal():
            self.max_index = CalcNode.parse(new_value)

        if (self.max_index is None) or (
                len(self.max_index.get_all_variables()) == 0 and self.max_index.evaluate() < CalcNode.parse(
                    new_value).evaluate()
        ):
            self.max_index = CalcNode.parse(new_value)
