from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render

from atcodertools.codegen.code_generators.universal_code_generator import UniversalCodeGenerator


def main(args: CodeGenArgs) -> str:
    code_parameters = UniversalCodeGenerator(
        args.format, args.config, args.config.code_generator_toml).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
