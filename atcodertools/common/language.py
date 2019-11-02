import re
from typing import Pattern, Callable

from atcodertools.codegen.code_generators import cpp, java, rust, python, nim, d, cs
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.tools.templates import get_default_template_path


class LanguageNotFoundError(Exception):
    pass


class CodeStyle:
    def __init__(self,
                 indent_width=None
                 ):
        self.indent_width = indent_width


class Language:
    def __init__(self,
                 name: str,
                 display_name: str,
                 extension: str,
                 submission_lang_pattern: Pattern[str],
                 default_code_generator: Callable[[CodeGenArgs], str],
                 default_template_path: str,
                 default_code_style=None,
                 compile_command=None
                 ):
        self.name = name
        self.display_name = display_name
        self.extension = extension
        self.submission_lang_pattern = submission_lang_pattern
        self.default_code_generator = default_code_generator
        self.default_template_path = default_template_path
        self.default_code_style = default_code_style
        self.compile_command = compile_command

    def source_code_name(self, name_without_extension: str) -> str:
        # put extension to the name
        return "{}.{}".format(name_without_extension, self.extension)

    def get_compile_command(self, filename: str):
        return self.compile_command.format(filename=filename)

    @classmethod
    def from_name(cls, name: str):
        for l in ALL_LANGUAGES:
            if l.name == name:
                return l
        raise LanguageNotFoundError(
            "No language support for '{}'".format(ALL_LANGUAGE_NAMES))


CPP = Language(
    name="cpp",
    display_name="C++",
    extension="cpp",
    submission_lang_pattern=re.compile(".*C\\+\\+14 \\(GCC.*"),
    default_code_generator=cpp.main,
    default_template_path=get_default_template_path('cpp'),
    compile_command="g++ {filename}.cpp -o {filename} -std=c++14"
)

JAVA = Language(
    name="java",
    display_name="Java",
    extension="java",
    submission_lang_pattern=re.compile(".*Java8.*"),
    default_code_generator=java.main,
    default_template_path=get_default_template_path('java'),
    compile_command="javac {filename}.java",
)

RUST = Language(
    name="rust",
    display_name="Rust",
    extension="rs",
    submission_lang_pattern=re.compile(".*Rust \\(1.*"),
    default_code_generator=rust.main,
    default_template_path=get_default_template_path('rs'),
    compile_command="rustc {filename}.rs -o {filename}"
)

PYTHON = Language(
    name="python",
    display_name="Python3",
    extension="py",
    submission_lang_pattern=re.compile(".*Python3.*"),
    default_code_generator=python.main,
    default_template_path=get_default_template_path('py'),
    compile_command="python3 -mpy_compile {filename}.py"
)

DLANG = Language(
    name="d",
    display_name="D",
    extension="d",
    submission_lang_pattern=re.compile(".*DMD64.*"),
    default_code_generator=d.main,
    default_template_path=get_default_template_path('d'),
    compile_command="dmd {filename}.d -of={filename}"
)

NIM = Language(
    name="nim",
    display_name="NIM",
    extension="nim",
    submission_lang_pattern=re.compile(".*Nim \\(0.*"),
    default_code_generator=nim.main,
    default_template_path=get_default_template_path('nim'),
    default_code_style=CodeStyle(indent_width=2),
    compile_command="nim cpp -o:{filename} {filename}.nim"
)

CSHARP = Language(
    name="cs",
    display_name="C#",
    extension="cs",
    submission_lang_pattern=re.compile(".*C# \\(Mono.*"),
    default_code_generator=cs.main,
    default_template_path=get_default_template_path('cs'),
    compile_command="mcs {filename}.cs -o {filename}"
)


ALL_LANGUAGES = [CPP, JAVA, RUST, PYTHON, NIM, DLANG, CSHARP]
ALL_LANGUAGE_NAMES = [lang.display_name for lang in ALL_LANGUAGES]
