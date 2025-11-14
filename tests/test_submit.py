import os
import unittest
from atcodertools.tools import submit

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_submit/"))


def fake_cookie_supplier():
    from http.cookiejar import Cookie
    return Cookie(
        version=0,
        name='REVEL_SESSION',
        value="@@@ invalid cookie @@@",
        port=None,
        port_specified=False,
        domain='atcoder.jp',
        domain_specified=True,
        domain_initial_dot=False,
        path='/',
        path_specified=True,
        secure=True,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False
    )


class TestTester(unittest.TestCase):

    def test_submit_fail_when_metadata_not_found(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "without_metadata")], fake_cookie_supplier, False)
        self.assertFalse(ok)

    def test_test_fail(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "with_metadata")], fake_cookie_supplier, False)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
