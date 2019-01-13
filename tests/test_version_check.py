import os
import unittest

from atcodertools.release_management.version_check import get_latest_version

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_tester/"))


class TestVersionCheck(unittest.TestCase):

    def test_get_latest_version_with_no_error(self):
        get_latest_version(use_cache=False)


if __name__ == '__main__':
    unittest.main()
