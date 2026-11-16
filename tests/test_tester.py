import argparse
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest
from colorama import Fore

from atcodertools.common.judgetype import MultiSolutionJudge
from atcodertools.common.language import ALL_LANGUAGES
from atcodertools.executils.run_program import ExecResult, ExecStatus
from atcodertools.tools import tester
from atcodertools.tools.compiler import compile_main_and_judge_programs
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.setter import main as setter_main
from atcodertools.tools.tester import (
    IrregularSampleFileError,
    TestSummary,
    build_details_str,
    infer_case_num,
    is_executable_file,
    str_to_bool,
)
from atcodertools.tools.utils import with_color
from tests.utils.toolchains import toolchain_available

RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./resources/test_tester/"))


class TestTester(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_multiple_exec_files(self) -> None:
        all_ok = tester.main("", ["-d", os.path.join(RESOURCE_DIR, "test_multiple_exec_files")])
        self.assertTrue(all_ok)

    def test_run_single_test(self) -> None:
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test")
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1"]))
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "2"]))

    def test_run_single_test_decimal_addition(self) -> None:
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test_decimal_addition")
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(
            tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "--judge-type", "absolute_or_relative"])
        )
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "relative"]))
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "-j", "relative"]))

    def test_run_single_test_decimal_multiplication(self) -> None:
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test_decimal_multiplication")
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(
            tester.main("", ["-d", test_dir, "-n", "2", "--error-value", "0.01", "-j", "absolute_or_relative"])
        )
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "absolute"]))
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "relative"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "-j", "relative"]))

    def test_run_single_test_decimal_mixed(self) -> None:
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test_decimal_mixed")
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "1", "-v", "0.0001", "-j", "absolute_or_relative"]))
        self.assertFalse(tester.main("", ["-d", test_dir, "-n", "2", "-v", "0.0001", "-j", "absolute_or_relative"]))

    @pytest.mark.requires_cpp
    def test_run_single_test_multisolution(self) -> None:
        test_dir = os.path.join(self.temp_dir, "test")
        shutil.copytree(os.path.join(RESOURCE_DIR, "test_run_single_test_multisolution"), test_dir)

        setter_main("", ["-d", test_dir, "-j", "multisolution"])
        metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
        self.assertTrue(isinstance(metadata.judge_method, MultiSolutionJudge))

        # Already set
        setter_main("", ["-d", test_dir, "--lang", "cpp"])
        metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
        assert metadata.lang is not None
        self.assertTrue(metadata.lang.name == "cpp")

        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-c", "True"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "2", "-c", "True"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "3", "-c", "True"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "4", "-c", "True"]))

    @pytest.mark.requires_cpp
    def test_run_single_test_interactive(self) -> None:
        test_dir = os.path.join(self.temp_dir, "test")
        shutil.copytree(os.path.join(RESOURCE_DIR, "test_run_single_test_interactive"), test_dir)

        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "1", "-j", "interactive", "-c", "True"]))
        self.assertTrue(tester.main("", ["-d", test_dir, "-n", "2", "-j", "interactive", "-c", "True"]))

    def test_compiler_and_tester(self) -> None:
        test_dir = os.path.join(self.temp_dir, "test")
        shutil.copytree(os.path.join(RESOURCE_DIR, "test_compiler_and_tester"), test_dir)

        tested_lang_count = 0
        for lang in ALL_LANGUAGES:
            if not toolchain_available(lang.name):
                continue
            tested_lang_count += 1
            setter_main("", ["--lang", lang.name, "-d", test_dir])
            metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
            compile_main_and_judge_programs(metadata, force_compile=True, cwd=test_dir)
            for i in [1, 2, 3, 4]:
                self.assertTrue(tester.main("", ["-d", test_dir, "-n", f"{i:d}", "-j", "normal"]))
        if tested_lang_count == 0:
            self.skipTest("no language toolchain available on this machine")

    @patch("os.access", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_is_executable_file(self, os_mock: MagicMock, is_file_mock: MagicMock) -> None:
        self.assertTrue(is_executable_file("a.out"))

    @patch("os.access", return_value=False)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_is_executable_file__not_executable(self, os_mock: MagicMock, is_file_mock: MagicMock) -> None:
        self.assertFalse(is_executable_file("a.out"))

    @patch("os.access", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_is_executable_file__source_code(self, os_mock: MagicMock, is_file_mock: MagicMock) -> None:
        self.assertFalse(is_executable_file("A.cpp"))

    @patch("os.access", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_is_executable_file__text(self, os_mock: MagicMock, is_file_mock: MagicMock) -> None:
        self.assertFalse(is_executable_file("in.txt"))

    @patch("os.access", return_value=True)
    @patch("pathlib.Path.is_file", return_value=False)
    def test_is_executable_file__directory(self, os_mock: MagicMock, is_file_mock: MagicMock) -> None:
        self.assertFalse(is_executable_file("directory"))

    @patch("platform.system", return_value="Windows")
    @patch("os.environ.get", return_value=".EXE;.out")
    def test_is_executable_file__windows(self, platform_system_mock: MagicMock, os_environ_get_mock: MagicMock) -> None:
        self.assertTrue(is_executable_file("A.eXe"))
        self.assertTrue(is_executable_file("A.out"))
        self.assertFalse(is_executable_file("A.exe.bak"))

    @patch("atcodertools.tools.tester.run_program", return_value=ExecResult(ExecStatus.NORMAL, "correct", "", 0))
    def test_run_for_samples(self, run_program_mock: MagicMock) -> None:
        io_mock = mock_open(read_data="correct")

        with patch("atcodertools.tools.tester.open", io_mock):
            self.assertEqual(TestSummary(1, False), tester.run_for_samples("a.out", [("in_1.txt", "out_1.txt")], 1))
            self.assertEqual(1, run_program_mock.call_count)

    @patch("atcodertools.tools.tester.build_details_str", return_value="")
    @patch("atcodertools.tools.tester.run_program", return_value=ExecResult(ExecStatus.NORMAL, "correct", "stderr", 0))
    def test_run_for_samples__with_stderr(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock) -> None:
        io_mock = mock_open(read_data="correct")

        with patch("atcodertools.tools.tester.open", io_mock):
            self.assertEqual(TestSummary(1, True), tester.run_for_samples("a.out", [("in_1.txt", "out_1.txt")], 1))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch("atcodertools.tools.tester.build_details_str", return_value="")
    @patch("atcodertools.tools.tester.run_program", return_value=ExecResult(ExecStatus.NORMAL, "wrong", "", 0))
    def test_run_for_samples__wrong_answer(
        self, run_program_mock: MagicMock, build_details_str_mock: MagicMock
    ) -> None:
        io_mock = mock_open(read_data="correct")

        with patch("atcodertools.tools.tester.open", io_mock):
            self.assertEqual(TestSummary(0, False), tester.run_for_samples("a.out", [("in_1.txt", "out_1.txt")], 1))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch("atcodertools.tools.tester.build_details_str", return_value="")
    @patch("atcodertools.tools.tester.run_program", return_value=ExecResult(ExecStatus.NORMAL, "wrong", "", 0))
    def test_run_for_samples__stop_execution_on_first_failure(
        self, run_program_mock: MagicMock, build_details_str_mock: MagicMock
    ) -> None:
        io_mock = mock_open(read_data="correct")

        with patch("atcodertools.tools.tester.open", io_mock):
            sample_pair_list = [("in_1.txt", "out_1.txt"), ("in_2.txt", "out_2.txt")]
            self.assertEqual(
                TestSummary(0, False), tester.run_for_samples("a.out", sample_pair_list, 1, knock_out=True)
            )
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch("atcodertools.tools.tester.build_details_str", return_value="")
    @patch("atcodertools.tools.tester.run_program", return_value=ExecResult(ExecStatus.NORMAL, "correct", "stderr", 0))
    def test_run_for_samples__skip_stderr(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock) -> None:
        io_mock = mock_open(read_data="correct")

        with patch("atcodertools.tools.tester.open", io_mock):
            self.assertEqual(
                TestSummary(1, True),
                tester.run_for_samples("a.out", [("in_1.txt", "out_1.txt")], 1, skip_io_on_success=True),
            )
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(0, build_details_str_mock.call_count)

    def test_build_details_str(self) -> None:
        in_out = "correct\n"
        output = "wrong\n"
        stderr = "stderr\n"
        expected = (
            with_color("[Input]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Expected]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Received]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + output
            + with_color("[Error]", Fore.LIGHTYELLOW_EX)
            + "\n"
            + stderr
        )
        io_mock = mock_open(read_data=in_out)

        with patch("atcodertools.tools.tester.open", io_mock):
            result = build_details_str(ExecResult(ExecStatus.NORMAL, output, stderr), "in.txt", "out.txt")
            self.assertEqual(expected, result)

    def test_build_details_str__show_testcase_if_there_is_stderr(self) -> None:
        in_out = "correct\n"
        stderr = "stderr\n"
        expected = (
            with_color("[Input]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Expected]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Received]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Error]", Fore.LIGHTYELLOW_EX)
            + "\n"
            + stderr
        )
        io_mock = mock_open(read_data=in_out)

        with patch("atcodertools.tools.tester.open", io_mock):
            result = build_details_str(ExecResult(ExecStatus.NORMAL, in_out, stderr), "in.txt", "out.txt")
            self.assertEqual(expected, result)

    def test_str_to_bool(self) -> None:
        for text in ("true", "True", "1", "yes"):
            self.assertTrue(str_to_bool(text), text)
        for text in ("false", "False", "0", "no"):
            self.assertFalse(str_to_bool(text), text)
        with self.assertRaises(argparse.ArgumentTypeError):
            str_to_bool("maybe")

    def test_infer_case_num(self) -> None:
        self.assertEqual(3, infer_case_num("in_3.txt"))
        self.assertEqual(12, infer_case_num("sample12.out"))
        with self.assertRaises(IrregularSampleFileError):
            infer_case_num("in_.txt")
        with self.assertRaises(IrregularSampleFileError):
            infer_case_num("output.txt")

    def test_build_details_str__on_runtime_failure(self) -> None:
        in_out = "correct\n"
        stderr = ""
        expected = (
            with_color("[Input]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Expected]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color("[Received]", Fore.LIGHTMAGENTA_EX)
            + "\n"
            + in_out
            + with_color(f"Aborted ({ExecStatus.RE.name})\n", Fore.LIGHTYELLOW_EX)
            + "\n"
        )
        io_mock = mock_open(read_data=in_out)

        with patch("atcodertools.tools.tester.open", io_mock):
            result = build_details_str(ExecResult(ExecStatus.RE, in_out, stderr), "in.txt", "out.txt")
            self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
