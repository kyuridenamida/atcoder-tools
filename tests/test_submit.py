import os
import unittest
from atcodertools.tools import submit

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_submit/"))


def fake_credential_suplier():
    return "@@fakeuser@@", "fakepass"


class TestTester(unittest.TestCase):

    def test_submit_fail_when_metadata_not_found(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "without_metadata")], fake_credential_suplier, False)
        self.assertFalse(ok)

    def test_test_fail(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "with_metadata")], fake_credential_suplier, False)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
