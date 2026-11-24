import os
import unittest
from unittest import mock

from atcodertools.client.models.submission import Submission
from atcodertools.tools import submit
from tests import requires_network

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


class FakeClient:
    def __init__(self):
        self.submitted_lang = None
        self.submitted_source = None

    def download_submission_list(self, contest):
        return []

    def submit_source_code(self, contest, problem, lang, source):
        self.submitted_lang = lang
        self.submitted_source = source
        return Submission(problem.problem_id, 12345)


class TestTester(unittest.TestCase):

    def test_submit_fail_when_metadata_not_found(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "without_metadata")], fake_cookie_supplier, False)
        self.assertFalse(ok)

    def _submit_with_fake_client(self, extra_args):
        client = FakeClient()
        with mock.patch("webbrowser.open") as mock_open:
            ok = submit.main(
                '',
                ['-d', os.path.join(RESOURCE_DIR, "with_metadata"),
                 '-f', '-u'] + extra_args,
                fake_cookie_supplier, False, client=client)
        return ok, client, mock_open

    def test_submit_uses_metadata_lang_by_default(self):
        ok, client, mock_open = self._submit_with_fake_client([])
        self.assertTrue(ok)
        self.assertEqual("cpp", client.submitted_lang.name)
        mock_open.assert_not_called()

    def test_submit_lang_option_overrides_metadata(self):
        ok, client, _ = self._submit_with_fake_client(['-l', 'python'])
        self.assertTrue(ok)
        self.assertEqual("python", client.submitted_lang.name)

    def test_submit_open_opens_submission_url(self):
        ok, client, mock_open = self._submit_with_fake_client(['--open'])
        self.assertTrue(ok)
        mock_open.assert_called_once()
        url = mock_open.call_args[0][0]
        self.assertIn("submissions/12345", url)

    @requires_network
    def test_test_fail(self):
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "with_metadata")], fake_cookie_supplier, False)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
