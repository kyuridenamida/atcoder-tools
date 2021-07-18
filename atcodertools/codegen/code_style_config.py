import importlib.machinery as imm
import os
from os.path import expanduser
from typing import Optional

from atcodertools.fileutils.normalize import normalize_path


INDENT_TYPE_SPACE = 'space'
INDENT_TYPE_TAB = 'tab'


class CodeStyleConfigInitError(Exception):
    pass


DEFAULT_WORKSPACE_DIR_PATH = os.path.join(expanduser("~"), "atcoder-workspace")


class CodeStyleConfig:

    def __init__(self,
                 indent_type: str = None,
                 indent_width: Optional[int] = None,
                 code_generator_file: Optional[str] = None,
                 code_generator_toml: Optional[str] = None,
                 template_file: Optional[str] = None,
                 workspace_dir: Optional[str] = None,
                 lang: str = "cpp",
                 ):
        from atcodertools.common.language import Language, LanguageNotFoundError, ALL_LANGUAGE_NAMES
        from atcodertools.codegen.code_generators import custom

        code_generator_file = normalize_path(code_generator_file)
        code_generator_toml = normalize_path(code_generator_toml)
        self.code_generator_toml = code_generator_toml
        template_file = normalize_path(template_file)

        try:
            lang = Language.from_name(lang)
        except LanguageNotFoundError:
            raise CodeStyleConfigInitError(
                "language must be one of {}".format(ALL_LANGUAGE_NAMES))

        if indent_type is not None and indent_type not in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]:
            raise CodeStyleConfigInitError(
                "indent_type must be 'space' or 'tab'")

        if indent_width is not None and indent_width < 0:
            raise CodeStyleConfigInitError(
                "indent_width must be a positive integer")

        if code_generator_file is not None and not os.path.exists(code_generator_file):
            raise CodeStyleConfigInitError(
                "Module file {} is not found".format(code_generator_file))

        if code_generator_toml is not None and not os.path.exists(code_generator_toml):
            raise CodeStyleConfigInitError(
                "TOML for Code Generator {} is not found".format(code_generator_toml))

        if template_file is not None and not os.path.exists(template_file):
            raise CodeStyleConfigInitError(
                "The specified template file '{}' is not found".format(
                    template_file)
            )
        if indent_type is not None:
            self.indent_type = indent_type
        elif lang.default_code_style is not None and lang.default_code_style.indent_type is not None:
            self.indent_type = lang.default_code_style.indent_type
        else:
            self.indent_type = INDENT_TYPE_SPACE

        if indent_width is not None:
            self.indent_width = indent_width
        elif lang.default_code_style is not None and lang.default_code_style.indent_width is not None:
            self.indent_width = lang.default_code_style.indent_width
        else:
            if self.indent_type == INDENT_TYPE_SPACE:
                self.indent_width = 4
            elif self.indent_type == INDENT_TYPE_TAB:
                self.indent_width = 1
            else:
                raise CodeStyleConfigInitError(
                    "indent_type must be 'space' or 'tab'")

        if code_generator_toml is not None:
            if code_generator_file is not None:
                raise CodeStyleConfigInitError(
                    "Both Code Generator File and Code Generator TOML is specified"
                )
            self.code_generator = custom.main
        elif code_generator_file is not None:
            try:
                module = imm.SourceFileLoader(
                    'code_generator', code_generator_file).load_module()
                self.code_generator = getattr(module, 'main')
            except AttributeError as e:
                raise CodeStyleConfigInitError(e, "Error while loading {}".format(
                    code_generator_file))
        else:
            self.code_generator = lang.default_code_generator

        self.template_file = normalize_path(
            template_file or lang.default_template_path)
        self.workspace_dir = normalize_path(
            workspace_dir or DEFAULT_WORKSPACE_DIR_PATH)
        self.lang = lang

    def indent(self, depth):
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        elif self.indent_type == INDENT_TYPE_TAB:
            return "\t" * self.indent_width * depth
        else:
            raise CodeStyleConfigInitError(
                "indent_type must be 'space' or 'tab'")
