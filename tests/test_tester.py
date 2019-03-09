import os
import unittest
from unittest.mock import patch, mock_open, MagicMock

from atcodertools.executils.run_program import ExecResult, ExecStatus
from atcodertools.tools import tester
from atcodertools.tools.tester import is_executable_file, TestSummary

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_tester/"))


class TestTester(unittest.TestCase):

    def test_multiple_exec_files(self):
        all_ok = tester.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "test_multiple_exec_files")])
        self.assertTrue(all_ok)

    def test_run_single_test(self):
        test_dir = os.path.join(RESOURCE_DIR, "test_run_single_test")
        self.assertTrue(tester.main('', ['-d', test_dir, "-n", "1"]))
        self.assertFalse(tester.main('', ['-d', test_dir, "-n", "2"]))

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

    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'correct', '', 0))
    def test_run_for_samples(self, run_program_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(1, False), tester.run_for_samples('a.out', [('in_1.txt', 'out_1.txt')], 1))
            run_program_mock.assert_called_once()

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'correct', 'stderr', 0))
    def test_run_for_samples__with_stderr(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(1, True), tester.run_for_samples('a.out', [('in_1.txt', 'out_1.txt')], 1))
            run_program_mock.assert_called_once()
            build_details_str_mock.assert_called_once()

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'wrong', '', 0))
    def test_run_for_samples__wrong_answer(self, run_program_mock: MagicMock, build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            self.assertEqual(TestSummary(0, False), tester.run_for_samples('a.out', [('in_1.txt', 'out_1.txt')], 1))
            run_program_mock.assert_called_once()
            build_details_str_mock.assert_called_once()

    @patch('atcodertools.tools.tester.build_details_str', return_value='')
    @patch('atcodertools.tools.tester.run_program', return_value=ExecResult(ExecStatus.NORMAL, 'wrong', '', 0))
    def test_run_for_samples__stop_execution_on_first_failure(self, run_program_mock: MagicMock,
                                                              build_details_str_mock: MagicMock):
        io_mock = mock_open(read_data='correct')

        with patch('atcodertools.tools.tester.open', io_mock):
            sample_pair_list = [('in_1.txt', 'out_1.txt'), ('in_2.txt', 'out_2.txt')]
            self.assertEqual(TestSummary(0, False), tester.run_for_samples('a.out', sample_pair_list, 1, True))
            run_program_mock.assert_called_once()
            build_details_str_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
