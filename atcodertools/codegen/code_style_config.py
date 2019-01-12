import importlib.machinery as imm
import os

from atcodertools.fileutils.normalize import normalize_path

INDENT_TYPE_SPACE = 'space'
INDENT_TYPE_TAB = 'tab'


class CodeStyleConfigInitError(Exception):
    pass


class CodeStyleConfig:

    def __init__(self,
                 indent_type: str = INDENT_TYPE_SPACE,
                 indent_width: int = 4,
                 code_generator_file: str = None,
                 template_file: str = None,
                 ):
        code_generator_file = normalize_path(code_generator_file)
        template_file = normalize_path(template_file)

        if indent_type not in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]:
            raise CodeStyleConfigInitError(
                "indent_type must be 'space' or 'tab'")

        if indent_width < 0:
            raise CodeStyleConfigInitError(
                "indent_width must be a positive integer")

        if code_generator_file is not None and not os.path.exists(code_generator_file):
            raise CodeStyleConfigInitError(
                "Module file {} is not found".format(code_generator_file))

        if template_file is not None and not os.path.exists(template_file):
            raise CodeStyleConfigInitError(
                "The specified template file '{}' is not found".format(
                    template_file)
            )

        self.indent_type = indent_type
        self.indent_width = indent_width
        self.code_generator = None

        if code_generator_file is not None:
            try:
                module = imm.SourceFileLoader(
                    'code_generator', code_generator_file).load_module()
                self.code_generator = getattr(module, 'main')
            except AttributeError as e:
                raise CodeStyleConfigInitError(e, "Error while loading {}".format(
                    code_generator_file))
        self.template_file = template_file

    def indent(self, depth):
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        return "\t" * self.indent_width * depth
