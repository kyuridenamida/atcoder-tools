import re
from typing import Pattern, Callable

from atcodertools.codegen.code_generators import cpp, java, rust, python, nim, d, cs, swift
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.tools.templates import get_default_template_path
import platform


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
                 compile_command=None,
                 test_command=None,
                 exec_filename=None
                 ):
        self.name = name
        self.display_name = display_name
        self.extension = extension
        self.submission_lang_pattern = submission_lang_pattern
        self.default_code_generator = default_code_generator
        self.default_template_path = default_template_path
        self.default_code_style = default_code_style
        self.compile_command = compile_command
        self.test_command = test_command
        self.code_filename = "{filename}." + extension
        if platform.system() == "Windows":
            self.exec_filename = exec_filename.replace(
                "{exec_extension}", ".exe")
        else:
            self.exec_filename = exec_filename.replace("{exec_extension}", "")

    def source_code_name(self, name_without_extension: str) -> str:
        # put extension to the name
        return "{}.{}".format(name_without_extension, self.extension)

    def get_compile_command(self, filename: str):
        return self.compile_command.format(filename=filename)

    def get_code_filename(self, filename: str):
        return self.code_filename.format(filename=filename)

    def get_exec_filename(self, filename: str):
        return self.exec_filename.format(filename=filename, capitalized_filename=filename.capitalize())

    def get_test_command(self, filename: str, cwd: str = '.'):
        exec_filename = cwd + '/'
        if platform.system() == "Windows":
            exec_filename += filename + ".exe"
        else:
            exec_filename += filename
        capitalized_filename = filename.capitalize()
        return self.test_command.format(filename=filename, exec_filename=exec_filename, capitalized_filename=capitalized_filename)

    @classmethod
    def from_name(cls, name: str):
        for lang in ALL_LANGUAGES:
            if lang.name == name:
                return lang
        raise LanguageNotFoundError(
            "No language support for '{}'".format(ALL_LANGUAGE_NAMES))


CPP = Language(
    name="cpp",
    display_name="C++",
    extension="cpp",
    submission_lang_pattern=re.compile(
        ".*C\\+\\+ \\(GCC 9.*|.*C\\+\\+14 \\(GCC 5.*"),
    default_code_generator=cpp.main,
    default_template_path=get_default_template_path('cpp'),
    compile_command="g++ {filename}.cpp -o {filename} -std=c++14",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)

JAVA = Language(
    name="java",
    display_name="Java",
    extension="java",
    submission_lang_pattern=re.compile(".*Java8.*|.*Java \\(OpenJDK 11.*"),
    default_code_generator=java.main,
    default_template_path=get_default_template_path('java'),
    compile_command="javac {filename}.java",
    test_command="java {capitalized_filename}",
    exec_filename="{capitalized_filename}.class"
)

RUST = Language(
    name="rust",
    display_name="Rust",
    extension="rs",
    submission_lang_pattern=re.compile(".*Rust \\(1.*"),
    default_code_generator=rust.main,
    default_template_path=get_default_template_path('rs'),
    compile_command="rustc {filename}.rs -o {filename}",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)

PYTHON = Language(
    name="python",
    display_name="Python",
    extension="py",
    submission_lang_pattern=re.compile(".*Python3.*|^Python$"),
    default_code_generator=python.main,
    default_template_path=get_default_template_path('py'),
    compile_command="python3 -mpy_compile {filename}.py",
    test_command="python3 {filename}.py",
    exec_filename="{filename}.pyc"
)

DLANG = Language(
    name="d",
    display_name="D",
    extension="d",
    submission_lang_pattern=re.compile(".*D \\(DMD.*"),
    default_code_generator=d.main,
    default_template_path=get_default_template_path('d'),
    compile_command="dmd {filename}.d -of={filename}",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)

NIM = Language(
    name="nim",
    display_name="NIM",
    extension="nim",
    submission_lang_pattern=re.compile(".*Nim \\(1.*"),
    default_code_generator=nim.main,
    default_template_path=get_default_template_path('nim'),
    default_code_style=CodeStyle(indent_width=2),
    compile_command="nim cpp -o:{filename} {filename}.nim",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)

CSHARP = Language(
    name="cs",
    display_name="C#",
    extension="cs",
    submission_lang_pattern=re.compile(".*C# \\(Mono.*"),
    default_code_generator=cs.main,
    default_template_path=get_default_template_path('cs'),
    compile_command="mcs {filename}.cs -o {filename}",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)

SWIFT = Language(
    name="swift",
    display_name="Swift",
    extension="swift",
    submission_lang_pattern=re.compile("^Swift"),
    default_code_generator=swift.main,
    default_template_path=get_default_template_path('swift'),
    compile_command="swiftc {filename}.swift -o {filename}",
    test_command="{exec_filename}",
    exec_filename="{filename}{exec_extension}"
)


ALL_LANGUAGES = [CPP, JAVA, RUST, PYTHON, NIM, DLANG, CSHARP, SWIFT]
ALL_LANGUAGE_NAMES = [lang.display_name for lang in ALL_LANGUAGES]
