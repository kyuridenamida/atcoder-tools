import importlib.machinery as imm
import os

INDENT_TYPE_SPACE = 'space'
INDENT_TYPE_TAB = 'tab'


class CodeStyleConfigInitError(Exception):
    pass


class CodeStyleConfig:

    def __init__(self,
                 indent_type: str = INDENT_TYPE_SPACE,
                 indent_width: int = 4,
                 code_gen_module_file: str = None,
                 ):

        if indent_type not in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]:
            raise CodeStyleConfigInitError(
                "indent_type must be 'space' or 'tab'")

        if indent_width < 0:
            raise CodeStyleConfigInitError(
                "indent_width must be a positive integer")

        if code_gen_module_file is not None and not os.path.exists(code_gen_module_file):
            raise CodeStyleConfigInitError(
                "Module file {} is not found".format(code_gen_module_file))

        self.indent_type = indent_type
        self.indent_width = indent_width
        self.code_gen_module = None

        if code_gen_module_file is not None:
            try:
                module = imm.SourceFileLoader(
                    'code_gen_module', code_gen_module_file).load_module()
                self.code_gen_module = getattr(module, 'main')
            except AttributeError as e:
                raise CodeStyleConfigInitError(e, "Error while loading {}".format(
                    code_gen_module_file))

    def indent(self, depth):
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        return "\t" * self.indent_width * depth
