import os
import tempfile
import time
import unittest
from functools import wraps

import requests

from atcodertools.client.atcoder import AtCoderClient, LoginError, save_cookie, load_cookie_to
from atcodertools.client.models.contest import Contest
from atcodertools.client.models.problem import Problem


def retry_once_on_failure(func):
    """Decorator to retry test on failure with 10 second wait"""
    @wraps(func)
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            print(f"Test failed, retrying in 10 seconds... Error: {e}")
            time.sleep(10)
            func(self)  # Retry once
    return wrapper


class TestAtCoderClientReal(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = AtCoderClient()
        # Wait 3 seconds before each test to reduce the traffic
        time.sleep(3)

    @retry_once_on_failure
    def test_submit_source_code(self):
        problem_list = self.client.download_problem_list(Contest("arc002"))
        self.assertEqual(
            ['arc002_1',
             'arc002_2',
             'arc002_3',
             'arc002_4'],
            [p.problem_id for p in problem_list])

    @retry_once_on_failure
    def test_download_problem_content(self):
        content = self.client.download_problem_content(
            Problem(Contest("arc002"), "C", "arc002_3"))
        self.assertEqual("N\nc_{1}c_{2}...c_{N}\n", content.input_format_text)
        self.assertEqual(3, len(content.samples))

    @retry_once_on_failure
    def test_login_failed(self):
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

        try:
            self.client.login(cookie_supplier=fake_cookie_supplier,
                              use_local_session_cache=False)
            self.fail("Unexpectedly, this test succeeded to login.")
        except LoginError:
            pass

    @retry_once_on_failure
    def test_download_all_contests(self):
        contests = self.client.download_all_contests()
        # Check if the number of contests is more than the number when I wrote
        # this unit test.
        self.assertGreaterEqual(len(contests), 523)

        # Make sure there is no duplication
        self.assertEqual(
            len(set([c.get_id() for c in contests])),
            len(contests))

    @retry_once_on_failure
    def test_check_logging_in_is_false(self):
        self.assertFalse(self.client.check_logging_in())

    @retry_once_on_failure
    def test_cookie_save_and_load(self):
        cookie_path = os.path.join(self.temp_dir, "cookie.txt")

        session = requests.Session()

        loaded = load_cookie_to(session, cookie_path)
        self.assertFalse(loaded)

        save_cookie(session, cookie_path)

        new_session = requests.Session()
        loaded = load_cookie_to(new_session, cookie_path)
        self.assertTrue(loaded)


if __name__ == "__main__":
    unittest.main()
