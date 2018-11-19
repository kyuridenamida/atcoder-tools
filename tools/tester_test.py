import unittest
from unittest.mock import patch

from tester import is_executable_file


class TestTester(unittest.TestCase):

    @patch('os.access', return_value=True)
    def test_is_executable_file(self, os_mock):
        self.assertTrue(is_executable_file('a.out'))

    @patch('os.access', return_value=False)
    def test_is_executable_file__file_is_not_executable(self, os_mock):
        self.assertFalse(is_executable_file('a.out'))

    @patch('os.access', return_value=True)
    def test_is_executable_file__file_is_source_code(self, os_mock):
        self.assertFalse(is_executable_file('A.cpp'))

    @patch('os.access', return_value=True)
    def test_is_executable_file__file_is_text(self, os_mock):
        self.assertFalse(is_executable_file('in.txt'))

    @patch('os.access', return_value=True)
    def test_is_executable_file__tester_itself(self, os_mock):
        self.assertFalse(is_executable_file('tester.py'))


if __name__ == '__main__':
    unittest.main()
