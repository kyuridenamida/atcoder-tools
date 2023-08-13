import unittest

from atcodertools.common.language import CPP, JAVA, RUST, PYTHON, DLANG, NIM, CSHARP, SWIFT, GO, JULIA

class TestTester(unittest.TestCase):
    def test_languages(self):
        language_compiler_map = {
            CPP: 'C++ 20 (gcc 12.2)',
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
