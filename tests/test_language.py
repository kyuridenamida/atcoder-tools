import unittest

from atcodertools.common.language import CPP, JAVA, RUST, PYTHON, DLANG, NIM, CSHARP, SWIFT, GO, JULIA


class TestLanguage(unittest.TestCase):
    def test_compilers(self):
        language_compiler_map = {
            CPP: 'C++23 (GCC 15.2.0)',
            JAVA: 'Java24 (OpenJDK 24.0.2)',
            RUST: 'Rust (rustc 1.89.0)',
            PYTHON: 'Python (CPython 3.13.7)',
            DLANG: 'D (DMD 2.111.0)',
            NIM: 'Nim (Nim 1.6.20)',
            CSHARP: 'C# 13.0 (.NET 9.0.8)',
            SWIFT: 'Swift 6.2',
            GO: 'Go (go 1.25.1)',
            JULIA: 'Julia (Julia 1.11.6)',
        }
        for language, compiler in language_compiler_map.items():
            self.assertRegex(compiler, language.submission_lang_pattern)

    # ABC429以前
    # TODO: 新ジャッジのみになったら消す
    def test_previous_compilers(self):
        language_compiler_map = {
            CPP: 'C++ 23 (gcc 12.2)',
            JAVA: 'Java (OpenJDK 17)',
            RUST: 'Rust (rustc 1.70.0)',
            PYTHON: 'Python (CPython 3.11.4)',
            DLANG: 'D (DMD 2.104.0)',
            NIM: 'Nim (Nim 1.6.14)',
            CSHARP: 'C# 11.0 (.NET 7.0.7)',
            SWIFT: 'Swift (swift 5.8.1)',
            GO: 'Go (go 1.20.6)',
            JULIA: 'Julia (Julia 1.9.2)',
        }
        for language, compiler in language_compiler_map.items():
            self.assertRegex(compiler, language.submission_lang_pattern)


if __name__ == '__main__':
    unittest.main()
