import os
import unittest
import shutil
import tempfile

from colorama import Fore
from unittest.mock import patch, mock_open, MagicMock

from atcodertools.executils.run_program import ExecResult, ExecStatus
from atcodertools.tools import tester
from atcodertools.tools.tester import is_executable_file, TestSummary, build_details_str
from atcodertools.tools.utils import with_color
from atcodertools.common.language import ALL_LANGUAGES
from atcodertools.tools.compiler import compile_main_and_judge_programs

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_tester/"))


class TestTester(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_multiple_exec_files(self):
        all_ok = tester.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "test_multiple_exec_files")])
        self.assertTrue(all_ok)

    def test_run_single_test(self):
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test")
        self.assertTrue(tester.main('', ['-d', test_dir, "-n", "1"]))
        self.assertFalse(tester.main('', ['-d', test_dir, "-n", "2"]))

    def test_run_single_test_decimal_addition(self):
        test_dir = os.path.join(
            RESOURCE_DIR, "test_run_single_test_decimal_addition")
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "2", "-v", "0.01", "--judge-type", "absolute_or_relative"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "2", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "relative"]))
        self.assertFalse(tester.main(
            '', ['-d', test_dir, "-n", "2", "-v", "0.01", "-j", "relative"]))

    def test_run_single_test_decimal_multiplication(self):
        test_dir = os.path.join(
            RESOURCE_DIR, "test_run_single_test_decimal_multiplication")
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "2", "--error-value", "0.01", "-j", "absolute_or_relative"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "absolute"]))
        self.assertFalse(tester.main(
            '', ['-d', test_dir, "-n", "2", "-v", "0.01", "-j", "absolute"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "1", "-v", "0.01", "-j", "relative"]))
        self.assertTrue(tester.main(
            '', ['-d', test_dir, "-n", "2", "-v", "0.01", "-j", "relative"]))

    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_is_executable_file(self, os_mock, is_file_mock):
        self.assertTrue(is_executable_file('a.out'))

    @patch('os.access', return_value=False)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_is_executable_file__not_executable(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('a.out'))

    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_is_executable_file__source_code(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('A.cpp'))

    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_is_executable_file__text(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('in.txt'))

    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=False)
    def test_is_executable_file__directory(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('directory'))

    @patch("platform.system", return_value="Windows")
    @patch("os.environ.get", return_value=".EXE;.out")
    def test_is_executable_file__windows(self, platform_system_mock, os_environ_get_mock):
        self.assertTrue(is_executable_file("A.eXe"))
        self.assertTrue(is_executable_file("A.out"))
        self.assertFalse(is_executable_file("A.exe.bak"))

    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'correct', '', 0))
    def test_run_for_samples(self, run_program_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(1, False), tester.run_for_samples(
                'a.out', [('in_1.txt', 'out_1.txt')], 1))
            self.assertEqual(1, run_program_mock.call_count)

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'correct', 'stderr', 0))
    def test_run_for_samples__with_stderr(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(1, True), tester.run_for_samples(
                'a.out', [('in_1.txt', 'out_1.txt')], 1))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'wrong', '', 0))
    def test_run_for_samples__wrong_answer(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(0, False), tester.run_for_samples(
                'a.out', [('in_1.txt', 'out_1.txt')], 1))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'wrong', '', 0))
    def test_run_for_samples__stop_execution_on_first_failure(self, run_program_mock: MagicMock,
                                                              build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            sample_pair_list = [('in_1.txt', 'out_1.txt'),
                                ('in_2.txt', 'out_2.txt')]
            self.assertEqual(TestSummary(0, False), tester.run_for_samples(
                'a.out', sample_pair_list, 1, knock_out=True))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(1, build_details_str_mock.call_count)

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'correct', 'stderr', 0))
    def test_run_for_samples__skip_stderr(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(1, True), tester.run_for_samples(
                'a.out', [('in_1.txt', 'out_1.txt')], 1, skip_io_on_success=True))
            self.assertEqual(1, run_program_mock.call_count)
            self.assertEqual(0, build_details_str_mock.call_count)

    def test_build_details_str(self):
        in_out = 'correct\n'
        output = 'wrong\n'
        stderr = 'stderr\n'
        expected = (with_color('[Input]', Fore.LIGHTMAGENTA_EX) + '\n'
                    + in_out + with_color('[Expected]',
                                          Fore.LIGHTMAGENTA_EX) + '\n' + in_out
                    + with_color('[Received]',
                                 Fore.LIGHTMAGENTA_EX) + '\n' + output
                    + with_color('[Error]', Fore.LIGHTYELLOW_EX) + '\n' + stderr)
        io_mock = mock_open(read_data=in_out)

        with patch('atcodertools.tools.tester.open', io_mock):
            result = build_details_str(ExecResult(
                ExecStatus.NORMAL, output, stderr), 'in.txt', 'out.txt')
            self.assertEqual(expected, result)

    def test_build_details_str__show_testcase_if_there_is_stderr(self):
        in_out = 'correct\n'
        stderr = 'stderr\n'
        expected = (with_color('[Input]', Fore.LIGHTMAGENTA_EX) + '\n'
                    + in_out + with_color('[Expected]',
                                          Fore.LIGHTMAGENTA_EX) + '\n' + in_out
                    + with_color('[Received]',
                                 Fore.LIGHTMAGENTA_EX) + '\n' + in_out
                    + with_color('[Error]', Fore.LIGHTYELLOW_EX) + '\n' + stderr)
        io_mock = mock_open(read_data=in_out)

        with patch('atcodertools.tools.tester.open', io_mock):
            result = build_details_str(ExecResult(
                ExecStatus.NORMAL, in_out, stderr), 'in.txt', 'out.txt')
            self.assertEqual(expected, result)

    def test_build_details_str__on_runtime_failure(self):
        in_out = 'correct\n'
        stderr = ''
        expected = (with_color('[Input]', Fore.LIGHTMAGENTA_EX) + '\n'
                    + in_out + with_color('[Expected]',
                                          Fore.LIGHTMAGENTA_EX) + '\n' + in_out
                    + with_color('[Received]',
                                 Fore.LIGHTMAGENTA_EX) + '\n' + in_out
                    + with_color('Aborted ({})\n'.format(ExecStatus.RE.name), Fore.LIGHTYELLOW_EX) + '\n')
        io_mock = mock_open(read_data=in_out)

        with patch('atcodertools.tools.tester.open', io_mock):
            result = build_details_str(ExecResult(
                ExecStatus.RE, in_out, stderr), 'in.txt', 'out.txt')
            self.assertEqual(expected, result)

    def test_compiler_and_tester(self):
        test_dir = os.path.join(self.temp_dir, "test1")
        shutil.copytree(os.path.join(
            RESOURCE_DIR, "test_compiler_and_tester"), test_dir)
        for i in [1, 2, 3, 4]:
            self.assertTrue(tester.main(
                '', ['-d', test_dir, "-n", "{:d}".format(i), "--compile-before-testing",
                     "-j", "normal",
                     "--compile-command", "g++ main.cpp -o main && touch compile{}".format(i)]))
        lst = os.listdir(test_dir)
        self.assertTrue("compile1" in lst)
        self.assertTrue("compile2" in lst)
        self.assertTrue("compile3" in lst)
        self.assertTrue("compile4" in lst)

        test_dir = os.path.join(self.temp_dir, "test2")
        shutil.copytree(os.path.join(
            RESOURCE_DIR, "test_compiler_and_tester"), test_dir)
        for i in [1, 2, 3, 4]:
            self.assertTrue(tester.main(
                '', ['-d', test_dir, "-n", "{:d}".format(i), "--compile-before-testing",
                     "--compile-only-when-diff-detected", "-j", "normal",
                     "--compile-command", "g++ main.cpp -o main && touch compile{}".format(i)]))
        lst = os.listdir(test_dir)
        self.assertTrue("compile1" in lst)
        self.assertTrue("compile2" not in lst)
        self.assertTrue("compile3" not in lst)
        self.assertTrue("compile4" not in lst)

        test_dir = os.path.join(self.temp_dir, "test3")
        shutil.copytree(os.path.join(
            RESOURCE_DIR, "test_compiler_and_tester"), test_dir)
        for i in [1, 2, 3, 4]:
            self.assertTrue(tester.main(
                '', ['-d', test_dir, "-n", "{:d}".format(i), "--compile-before-testing",
                     "--compile-only-when-diff-detected", "-j", "normal",
                     "--compile-command", "g++ main.cpp -o main && touch compile{}".format(i)]))
            os.chdir(test_dir)
            os.system('echo // >> main.cpp')
        lst = os.listdir(test_dir)
        self.assertTrue("compile1" in lst)
        self.assertTrue("compile2" in lst)
        self.assertTrue("compile3" in lst)
        self.assertTrue("compile4" in lst)

    def test_compiler_and_tester_for_each_lang(self):
        test_dir = os.path.join(self.temp_dir, "test")
        shutil.copytree(os.path.join(
            RESOURCE_DIR, "test_compiler_and_tester_for_each_lang"), test_dir)

        for lang in ALL_LANGUAGES:
            lang_dir = os.path.join(test_dir, lang.name)

            compile_main_and_judge_programs(
                lang, force_compile=True, cwd=lang_dir)
            for i in [1, 2, 3, 4]:
                self.assertTrue(tester.main(
                    '', ['-d', lang_dir, "-n", "{:d}".format(i), "--compile-before-testing", "-j", "normal"]))


if __name__ == '__main__':
    unittest.main()
