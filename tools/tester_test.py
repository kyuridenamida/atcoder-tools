import unittest
from unittest.mock import patch

from tester import is_executable_file, remove_last_newline


class TestTester(unittest.TestCase):

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
    @patch('pathlib.Path.is_file', return_value=True)
    def test_is_executable_file__tester_itself(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('tester.py'))

    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=False)
    def test_is_executable_file__directory(self, os_mock, is_file_mock):
        self.assertFalse(is_executable_file('directory'))

    def test_remove_last_newline(self):
        self.assertEqual('ans1\nans2', remove_last_newline('ans1\nans2\n'))

    def test_remove_last_newline__no_newline_at_end(self):
        self.assertEqual('ans1\nans2', remove_last_newline('ans1\nans2'))

    def test_remove_last_newline__remove_only_one_newline(self):
        self.assertEqual('ans\n', remove_last_newline('ans\n\n'))


if __name__ == '__main__':
    unittest.main()
