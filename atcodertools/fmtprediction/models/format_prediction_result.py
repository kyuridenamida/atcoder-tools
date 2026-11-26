from typing import Dict, Optional

from atcodertools.fmtprediction.models.format import (
    Format,
    RepeatedCaseFormat,
)
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import (
    Variable,
    SimpleVariable,
)
from atcodertools.fmtprediction.models.ragged_format import (
    RaggedRowFormat,
    create_typed_ragged_row_pattern,
)
from atcodertools.fmtprediction.models.homogeneous_query_format import (
    HomogeneousQueryFormat,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
)


class FormatPredictionResult:
    def __init__(
        self,
        format_: Optional[Format[Variable]] = None,
    ):
        self.format = format_

    @staticmethod
    def _create_typed_format(
        simple_format: Format[SimpleVariable],
        var_to_type: Dict[str, Type],
    ) -> Format[Variable]:
        var_to_info = {}

        for var in simple_format.all_vars():
            assert var.name not in var_to_info

            var_to_info[var.name] = Variable(
                var.name,
                var.first_index,
                var.second_index,
                var_to_type[var.name],
                third_index=var.third_index,
            )

        typed_format = Format()

        for pattern in simple_format.sequence:
            typed_format.push_back(
                pattern.with_replaced_vars(
                    var_to_info
                )
            )

        return typed_format

    @classmethod
    def create_typed_format(
        cls,
        simple_format: Format[SimpleVariable],
        var_to_type: Dict[str, Type],
    ):
        return FormatPredictionResult(
            cls._create_typed_format(
                simple_format,
                var_to_type,
            )
        )

    @classmethod
    def create_ragged_row_typed_format(
        cls,
        prefix_format,
        schema,
        var_to_type,
        suffix_format=None,
    ):
        typed_prefix = cls._create_typed_format(
            prefix_format,
            var_to_type,
        )

        if suffix_format is None:
            suffix_format = Format()

        typed_suffix = cls._create_typed_format(
            suffix_format,
            var_to_type,
        )

        ragged_pattern = (
            create_typed_ragged_row_pattern(
                schema,
                var_to_type,
            )
        )

        return FormatPredictionResult(
            RaggedRowFormat(
                typed_prefix,
                ragged_pattern,
                typed_suffix,
            )
        )

    @classmethod
    def create_tagged_query_typed_format(
        cls,
        format_,
        var_to_type,
    ):
        typed_prefix = cls._create_typed_format(
            format_.prefix_format,
            var_to_type,
        )

        return FormatPredictionResult(
            TaggedQueryFormat(
                typed_prefix,
                format_.query_count_var,
                format_.variants,
                format_.query_collection_name,
            )
        )

    @classmethod
    def create_homogeneous_query_typed_format(
        cls,
        format_,
        var_to_type,
    ):
        typed_prefix = cls._create_typed_format(
            format_.prefix_format,
            var_to_type,
        )

        return FormatPredictionResult(
            HomogeneousQueryFormat(
                typed_prefix,
                format_.query_count_var,
                format_.arguments,
                format_.query_collection_name,
            )
        )

    @classmethod
    def create_repeated_case_typed_format(
        cls,
        prefix_format: Format[SimpleVariable],
        case_format: Format[SimpleVariable],
        case_count_var: str,
        var_to_type: Dict[str, Type],
    ):
        typed_prefix = cls._create_typed_format(
            prefix_format,
            var_to_type,
        )
        typed_case = cls._create_typed_format(
            case_format,
            var_to_type,
        )

        return FormatPredictionResult(
            RepeatedCaseFormat(
                typed_prefix,
                typed_case,
                case_count_var,
            )
        )

    @classmethod
    def empty_result(cls):
        return FormatPredictionResult()
