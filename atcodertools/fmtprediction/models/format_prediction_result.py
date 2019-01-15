from typing import Dict, Optional

from atcodertools.fmtprediction.models.format import Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable, SimpleVariable


class FormatPredictionResult:

    def __init__(self, format_: Optional[Format[Variable]] = None):
        self.format = format_

    @classmethod
    def create_typed_format(cls, simple_format: Format[SimpleVariable], var_to_type: Dict[str, Type]):
        var_to_info = {}
        for var in simple_format.all_vars():
            assert var.name not in var_to_info
            var_to_info[var.name] = Variable(
                var.name,
                var.first_index,
                var.second_index,
                var_to_type[var.name]
            )

        fmt = Format()  # type: Format[Variable]

        for pattern in simple_format.sequence:
            fmt.push_back(pattern.with_replaced_vars(var_to_info))

        return FormatPredictionResult(fmt)

    @classmethod
    def empty_result(cls):
        return FormatPredictionResult()
