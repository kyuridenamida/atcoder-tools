import os
import tempfile
import unittest
import shutil
from typing import Dict

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.client.models.contest import Contest
from atcodertools.client.models.problem import Problem
from atcodertools.common.language import CPP
from atcodertools.tools import submit

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_atcoder_client_mock/")


class MockResponse:

    def __init__(self, text=None, url=None):
        self.text = text
        self.url = url

    @classmethod
    def response_from(cls, filename):
        with open(filename, 'r') as f:
            return MockResponse(text=f.read())


def fake_resp(filename: str):
    return MockResponse.response_from(os.path.join(RESOURCE_DIR, filename))


def create_fake_request_func(get_url_to_resp: Dict[str, MockResponse] = None,
                             post_url_to_resp: Dict[str, MockResponse] = None,
                             ):
    def func(url, method="GET", **kwargs):
        if method == "GET":
            return get_url_to_resp.get(url)
        return post_url_to_resp.get(url)

    return func


def restore_client_after_run(func):
    def test_decorated(*args, **kwargs):
        client = AtCoderClient()
        prev = client._request
        func(*args, **kwargs)
        client._request = prev

    return test_decorated


class TestAtCoderClientMock(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = AtCoderClient()

    @restore_client_after_run
    def test_download_submission_list(self):
        contest = Contest("arc001")
        self.client._request = create_fake_request_func(
            {
                contest.get_my_submissions_url(1): fake_resp("my_submissions/1.html"),
                contest.get_my_submissions_url(2): fake_resp("my_submissions/2.html"),
                contest.get_my_submissions_url(3): fake_resp("my_submissions/3.html"),
                contest.get_my_submissions_url(4): fake_resp("my_submissions/4.html")
            }
        )
        submissions = self.client.download_submission_list(Contest("arc001"))
        submission_ids = [x.submission_id for x in submissions]
        self.assertEqual(50, len(submission_ids))
        self.assertEqual(sorted(submission_ids, reverse=True), submission_ids)

    @restore_client_after_run
    def test_submit_source_code(self):
        contest = Contest("arc001")
        problem = Problem(contest, "A", "arc001_1")

        self.client._request = create_fake_request_func(
            {contest.get_submit_url(): fake_resp("submit/after_get.html")},
            {contest.get_submit_url(): fake_resp("submit/after_post.html")}
        )

        # test two patterns (str, Language object) for parameter lang
        for lang in [CPP, "C++ 20 (gcc 12.2)"]:
            submission = self.client.submit_source_code(
                contest, problem, lang, "x")
            self.assertEqual(13269587, submission.submission_id)
            self.assertEqual("arc001_1", submission.problem_id)

    @restore_client_after_run
    def test_login_success(self):
        self.client._request = create_fake_request_func(
            post_url_to_resp={
                "https://atcoder.jp/login": fake_resp("after_login.html")
            }
        )

        def fake_supplier():
            return "@@@ invalid user name @@@", "@@@ password @@@"

        self.client.login(credential_supplier=fake_supplier,
                          use_local_session_cache=False)

    @restore_client_after_run
    def test_check_logging_in_success(self):
        setting_url = "https://atcoder.jp/home"
        self.client._request = create_fake_request_func(
            {setting_url: fake_resp("after_login.html")},
        )
        self.assertTrue(self.client.check_logging_in())

    @restore_client_after_run
    def test_check_logging_in_fail(self):
        setting_url = "https://atcoder.jp/home"
        self.client._request = create_fake_request_func(
            {setting_url: fake_resp("before_login.html")}
        )
        self.assertFalse(self.client.check_logging_in())

    @restore_client_after_run
    def test_exec_on_submit(self):
        global submitted_source_code
        submitted_source_code = None

        def create_fake_request_func_for_source(get_url_to_resp: Dict[str, MockResponse] = None,
                                                post_url_to_resp: Dict[str,
                                                                       MockResponse] = None,
                                                ):
            global submitted_source_code

            def func(url, method="GET", **kwargs):
                global submitted_source_code
                if method == "GET":
                    return get_url_to_resp.get(url)
                submitted_source_code = kwargs["data"]['sourceCode']
                return post_url_to_resp.get(url)
            return func

        contest = Contest("abc215")

        self.client._request = create_fake_request_func_for_source(
            {contest.get_submit_url(): fake_resp("submit/after_get.html")},
            {contest.get_submit_url(): fake_resp("submit/after_post.html")}
        )

        test_dir = os.path.join(self.temp_dir, "exec_on_submit")
        shutil.copytree(os.path.join(RESOURCE_DIR, "exec_on_submit"), test_dir)
        config_path = os.path.join(test_dir, "config.toml")

        submit.main('', ["--dir", test_dir, "--config",
                    config_path, "-f", "-u"], client=self.client)
        self.assertTrue(os.path.exists(os.path.join(
            test_dir, "exec_before_submit_is_completed")))
        self.assertEqual(submitted_source_code, "Kyuuridenamida\n")
        self.assertTrue(os.path.exists(os.path.join(
            test_dir, "exec_after_submit_is_completed")))


if __name__ == "__main__":
    unittest.main()
