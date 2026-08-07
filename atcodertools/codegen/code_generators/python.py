from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render

from atcodertools.codegen.code_generators.universal_code_generator import (
    UniversalCodeGenerator,
    get_builtin_code_generator_info_toml_path,
)
from atcodertools.fmtprediction.models.tagged_query_format import (
    TaggedQueryFormat,
)
from atcodertools.codegen.tagged_query_python_generator import (
    TaggedQueryPythonGenerator,
)


def _append_argument(
    current,
    additional,
):
    if current:
        return "{}, {}".format(
            current,
            additional,
        )

    return additional


def _normalize_fragment(
    fragment,
    base_indent,
):
    lines = fragment.splitlines()

    if not lines:
        return ""

    result = [
        lines[0],
    ]

    for line in lines[1:]:
        if line.startswith(base_indent):
            line = line[
                len(base_indent):
            ]

        result.append(line)

    return "\n".join(result)


def _tagged_query_parameters(
    args,
    information_path,
):
    prefix_generator = (
        UniversalCodeGenerator(
            args.format.prefix_format,
            args.config,
            information_path,
        )
    )

    prefix_parameters = (
        prefix_generator
        .generate_parameters()
    )

    if not prefix_parameters[
        "prediction_success"
    ]:
        return prefix_parameters

    base_indent = args.config.indent(1)

    normalized_prefix = (
        _normalize_fragment(
            prefix_parameters[
                "input_part"
            ],
            base_indent,
        )
    )

    tagged_generator = (
        TaggedQueryPythonGenerator(
            args.format,
            normalized_prefix,
        )
    )

    nested_input_part = (
        tagged_generator
        .generate_input_part(
            indent=base_indent,
        )
    )

    if not nested_input_part.startswith(
        base_indent
    ):
        raise ValueError(
            "tagged-query input fragment "
            "does not start with base indent"
        )

    input_part = nested_input_part[
        len(base_indent):
    ]

    collection = (
        args.format
        .query_collection_name
    )

    parameters = dict(
        prefix_parameters
    )

    parameters.update(
        formal_arguments=(
            _append_argument(
                prefix_parameters[
                    "formal_arguments"
                ],
                "{}: List[Tuple]".format(
                    collection
                ),
            )
        ),
        actual_arguments=(
            _append_argument(
                prefix_parameters[
                    "actual_arguments"
                ],
                collection,
            )
        ),
        input_part=input_part,
        prefix_input_part=(
            prefix_parameters[
                "input_part"
            ]
        ),
        case_input_part="",
        global_declaration="",
        global_input_part="",
        multi_case=False,
        case_count_var=None,
        case_loop_var=None,
        tagged_query=True,
        query_collection_name=collection,
        prediction_success=True,
    )

    return parameters


def main(args: CodeGenArgs) -> str:
    information_path = (
        get_builtin_code_generator_info_toml_path(
            "python"
        )
    )

    if isinstance(
        args.format,
        TaggedQueryFormat,
    ):
        code_parameters = (
            _tagged_query_parameters(
                args,
                information_path,
            )
        )
    else:
        code_parameters = (
            UniversalCodeGenerator(
                args.format,
                args.config,
                information_path,
            )
            .generate_parameters()
        )

    return render(
        args.template,
        config=args.config,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
