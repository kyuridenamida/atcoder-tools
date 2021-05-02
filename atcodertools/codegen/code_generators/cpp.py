from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render

<<<<<<< HEAD
from atcodertools.codegen.code_generators.universal_code_generator import UniversalCodeGenerator


def main(args: CodeGenArgs) -> str:
    code_parameters = UniversalCodeGenerator(
        args.format, args.config, "cpp").generate_parameters()
=======
from atcodertools.codegen.code_generators.universal_code_generator import CodeGenerator
from atcodertools.codegen.code_generators.universal_generator.cpp import CodeGeneratorInfo


def main(args: CodeGenArgs) -> str:
    code_parameters = CodeGenerator(
        args.format, args.config, CodeGeneratorInfo()).generate_parameters()
>>>>>>> 42186c678e4df69fe3092c45c9db231ac701a3c7
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        **code_parameters
    )
