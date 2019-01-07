from typing import Optional

from atcodertools.fmtprediction.models.index import Index
from atcodertools.fmtprediction.models.type import Type


class SimpleVariable:

    def __init__(self,
                 name: str,
                 first_index: Optional[Index],
                 second_index: Optional[Index]):
        self.name = name
        self.first_index = first_index
        self.second_index = second_index

    def dim_num(self):
        if self.second_index:
            return 2
        if self.first_index:
            return 1
        return 0

    @classmethod
    def create(cls, name: str, dim_num: int):
        assert dim_num <= 2

        first_index = None
        second_index = None

        if dim_num >= 2:
            second_index = Index()
        if dim_num >= 1:
            first_index = Index()

        return SimpleVariable(name, first_index, second_index)


class Variable(SimpleVariable):

    """
        SimpleVariable + type information
    """

    def __init__(self,
                 name: str,
                 first_index: Optional[Index],
                 second_index: Optional[Index],
                 type_: Type):
        super().__init__(name, first_index, second_index)
        self.type = type_
