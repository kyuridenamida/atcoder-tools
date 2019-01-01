import os
import unittest
from unittest.mock import patch

from atcodertools.release_management.version_check import get_latest_version, _fetch_latest_version
from atcodertools.tools import tester
from atcodertools.tools.tester import is_executable_file

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_tester/"))


class TestTester(unittest.TestCase):
    def test_get_latest_version_with_no_error(self):
        get_latest_version(user_cache=False)


if __name__ == '__main__':
    unittest.main()
