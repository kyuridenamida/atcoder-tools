from collections import OrderedDict
from typing import Dict

from atcodertools.models.analyzer.simple_format import SimpleFormat
from atcodertools.models.predictor.variable import Variable


class FormatPredictionResult:

    def __init__(self, simple_format: SimpleFormat, var_to_type: Dict[str, type]):
        self.simple_format = simple_format
        self.var_to_info = OrderedDict()
        for var in simple_format.all_vars():
            assert var.var_name not in self.var_to_info
            self.var_to_info[var.var_name] = Variable(
                var, var_to_type[var.var_name])
