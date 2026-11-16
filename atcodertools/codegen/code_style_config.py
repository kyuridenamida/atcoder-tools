import importlib.util
import os
from os.path import expanduser
from typing import TYPE_CHECKING, Callable, Optional

from atcodertools.fileutils.normalize import normalize_path

if TYPE_CHECKING:
    from atcodertools.codegen.models.code_gen_args import CodeGenArgs

INDENT_TYPE_SPACE = "space"
INDENT_TYPE_TAB = "tab"


class CodeStyleConfigInitError(Exception):
    pass


DEFAULT_WORKSPACE_DIR_PATH = os.path.join(expanduser("~"), "atcoder-workspace")
DEFAULT_LANGUAGE = "cpp"


class CodeStyleConfig:
    def __init__(
        self,
        indent_type: str = INDENT_TYPE_SPACE,
        indent_width: Optional[int] = None,
        code_generator_file: Optional[str] = None,
        template_file: Optional[str] = None,
        workspace_dir: Optional[str] = None,
        lang: str = DEFAULT_LANGUAGE,
    ) -> None:
        from atcodertools.common.language import ALL_LANGUAGE_NAMES, Language, LanguageNotFoundError

        code_generator_file = normalize_path(code_generator_file)
        template_file = normalize_path(template_file)

        try:
            language = Language.from_name(lang)
        except LanguageNotFoundError as e:
            raise CodeStyleConfigInitError(f"language must be one of {ALL_LANGUAGE_NAMES}") from e

        if indent_type not in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]:
            raise CodeStyleConfigInitError("indent_type must be 'space' or 'tab'")

        if indent_width is not None and indent_width < 0:
            raise CodeStyleConfigInitError("indent_width must be a positive integer")

        if code_generator_file is not None and not os.path.exists(code_generator_file):
            raise CodeStyleConfigInitError(f"Module file {code_generator_file} is not found")

        if template_file is not None and not os.path.exists(template_file):
            raise CodeStyleConfigInitError(f"The specified template file '{template_file}' is not found")

        self.indent_type = indent_type

        if indent_width is not None:
            self.indent_width = indent_width
        elif language.default_code_style is not None and language.default_code_style.indent_width is not None:
            self.indent_width = language.default_code_style.indent_width
        else:
            self.indent_width = 4

        if code_generator_file is not None:
            try:
                spec = importlib.util.spec_from_file_location("code_generator", code_generator_file)
                assert spec is not None
                assert spec.loader is not None
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.code_generator: Callable[[CodeGenArgs], str] = module.main
            except AttributeError as e:
                raise CodeStyleConfigInitError(e, f"Error while loading {code_generator_file}") from e
        else:
            self.code_generator = language.default_code_generator

        self.template_file = normalize_path(template_file or language.default_template_path)
        self.workspace_dir = normalize_path(workspace_dir or DEFAULT_WORKSPACE_DIR_PATH)
        self.lang = language

    def indent(self, depth: int) -> str:
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        return "\t" * self.indent_width * depth
