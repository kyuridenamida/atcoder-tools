from collections import OrderedDict
from typing import Dict

from atcodertools.models.predictor.simple_format import SimpleFormat
from atcodertools.models.predictor.type import Type
from atcodertools.models.predictor.variable import Variable


class FormatPredictionResult:

    def __init__(self, simple_format: SimpleFormat, var_to_type: Dict[str, Type]):
        self.simple_format = simple_format
        self.var_to_info = OrderedDict()
        for var in simple_format.all_vars():
            assert var.name not in self.var_to_info
            self.var_to_info[var.name] = Variable(
                var.name,
                var.first_index,
                var.second_index,
                var_to_type[var.name]
            )
