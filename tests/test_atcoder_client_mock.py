import contextlib
import os
import tempfile
import unittest
from typing import Any, Callable, ContextManager, Dict, List, Optional, Tuple, Union

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.client.models.contest import Contest
from atcodertools.client.models.problem import Problem
from atcodertools.common.language import CPP, Language

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_atcoder_client_mock/")


class MockResponse:

    def __init__(self, text: Optional[str]=None, url: Optional[str]=None) -> None:
        self.text = text
        self.url = url

    @classmethod
    def response_from(cls, filename: str) -> "MockResponse":
        with open(filename, 'r') as f:
            return MockResponse(text=f.read())


def fake_resp(filename: str) -> MockResponse:
    return MockResponse.response_from(os.path.join(RESOURCE_DIR, filename))


def create_fake_request_func(get_url_to_resp: Optional[Dict[str, MockResponse]] = None,
                             post_url_to_resp: Optional[Dict[str, MockResponse]] = None,
                             ) -> Callable[..., Optional[MockResponse]]:
    def func(url: str, method: str="GET", **kwargs: Any) -> Optional[MockResponse]:
        if method == "GET":
            return (get_url_to_resp or {}).get(url)
        return (post_url_to_resp or {}).get(url)

    return func


def restore_client_after_run(func: Callable[..., None]) -> Callable[..., None]:
    def test_decorated(*args: Any, **kwargs: Any) -> None:
        client = AtCoderClient()
        prev = client._request
        try:
            func(*args, **kwargs)
        finally:
            client._request = prev  # type: ignore[method-assign]

    return test_decorated


class TestAtCoderClientMock(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.client = AtCoderClient()

    @restore_client_after_run
    def test_download_submission_list(self) -> None:
        contest = Contest("arc001")
        self.client._request = create_fake_request_func(  # type: ignore[method-assign, assignment]
            {
                contest.get_my_submissions_url(1): fake_resp("my_submissions/1.html"),
                contest.get_my_submissions_url(2): fake_resp("my_submissions/2.html"),
                contest.get_my_submissions_url(3): fake_resp("my_submissions/3.html")
            }
        )
        submissions = self.client.download_submission_list(Contest("arc001"))
        submission_ids = [x.submission_id for x in submissions]
        self.assertEqual(33, len(submission_ids))
        self.assertEqual(sorted(submission_ids, reverse=True), submission_ids)

    @restore_client_after_run
    def test_submit_source_code(self) -> None:
        contest = Contest("arc001")
        problem = Problem(contest, "A", "arc001_1")

        self.client._request = create_fake_request_func(  # type: ignore[method-assign, assignment]
            {contest.get_submit_url(): fake_resp("submit/after_get.html")},
            {contest.get_submit_url(): fake_resp("submit/after_post.html")}
        )

        # test two patterns (str, Language object) for parameter lang
        langs: List[Union[Language, str]] = [CPP, "C++14 (GCC 5.4.1)"]
        for lang in langs:
            if isinstance(lang, str):
                # passing lang as a str is deprecated and must warn
                ctx: ContextManager[object] = self.assertWarns(UserWarning)
            else:
                ctx = contextlib.nullcontext()
            with ctx:
                submission = self.client.submit_source_code(
                    contest, problem, lang, "x")
            self.assertEqual(3905485, submission.submission_id)
            self.assertEqual("arc001_1", submission.problem_id)

    @restore_client_after_run
    def test_login_success(self) -> None:
        self.client._request = create_fake_request_func(  # type: ignore[method-assign, assignment]
            {
                "https://atcoder.jp/login": fake_resp("login.html")
            },
            {
                "https://atcoder.jp/login": fake_resp("after_login.html")
            }
        )

        def fake_supplier() -> Tuple[str, str]:
            return "@@@ invalid user name @@@", "@@@ password @@@"

        self.client.login(credential_supplier=fake_supplier,
                          use_local_session_cache=False)

    @restore_client_after_run
    def test_check_logging_in_success(self) -> None:
        self.client._request = create_fake_request_func(  # type: ignore[method-assign, assignment]
            {
                "https://atcoder.jp/home": fake_resp("home_logged_in.html")
            }
        )
        self.assertTrue(self.client.check_logging_in())

    @restore_client_after_run
    def test_check_logging_in_failure(self) -> None:
        self.client._request = create_fake_request_func(  # type: ignore[method-assign, assignment]
            {
                "https://atcoder.jp/home": MockResponse(text="<html><body>Sign In</body></html>")
            }
        )
        self.assertFalse(self.client.check_logging_in())


if __name__ == "__main__":
    unittest.main()
