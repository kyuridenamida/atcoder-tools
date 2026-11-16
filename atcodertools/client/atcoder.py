import getpass
import os
import re
import warnings
from http.cookiejar import LWPCookieJar
from re import Pattern
from typing import Any, Callable, Optional, Union, cast

import requests
from bs4 import BeautifulSoup

from atcodertools.client.models.contest import Contest as Contest
from atcodertools.client.models.problem import Problem
from atcodertools.client.models.problem_content import ProblemContent as ProblemContent
from atcodertools.client.models.problem_content import get_problem_content as get_problem_content
from atcodertools.client.models.submission import Submission
from atcodertools.common.language import Language
from atcodertools.common.logging import logger
from atcodertools.fileutils.artifacts_cache import get_cache_file_path


class LoginError(Exception):
    pass


default_cookie_path = get_cache_file_path("cookie.txt")


def save_cookie(session: requests.Session, cookie_path: Optional[str] = None) -> None:
    cookie_path = cookie_path or default_cookie_path
    os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
    cookies = cast(LWPCookieJar, session.cookies)
    cookies.save()
    logger.info(f"Saved session into {os.path.abspath(cookie_path)}")
    os.chmod(cookie_path, 0o600)


def load_cookie_to(session: requests.Session, cookie_path: Optional[str] = None) -> bool:
    cookie_path = cookie_path or default_cookie_path
    jar = LWPCookieJar(cookie_path)
    session.cookies = jar  # type: ignore[assignment]
    if os.path.exists(cookie_path):
        jar.load()
        logger.info(f"Loaded session from {os.path.abspath(cookie_path)}")
        return True
    return False


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def default_credential_supplier() -> tuple[str, str]:
    username = input("AtCoder username: ")
    password = getpass.getpass("AtCoder password: ")
    return username, password


class AtCoderClient(metaclass=Singleton):
    def __init__(self) -> None:
        self._session = requests.Session()

    def check_logging_in(self) -> bool:
        private_url = "https://atcoder.jp/home"
        resp = self._request(private_url)
        return resp.text.find("Sign In") == -1

    def login(
        self,
        credential_supplier: Optional[Callable[[], tuple[str, str]]] = None,
        use_local_session_cache: bool = True,
        save_session_cache: bool = True,
    ) -> None:

        if credential_supplier is None:
            credential_supplier = default_credential_supplier

        if use_local_session_cache:
            load_cookie_to(self._session)
            if self.check_logging_in():
                logger.info("Successfully Logged in using the previous session cache.")
                logger.info(f"If you'd like to invalidate the cache, delete {default_cookie_path}.")

                return

        username, password = credential_supplier()

        soup = BeautifulSoup(self._request("https://atcoder.jp/login").text, "html.parser")
        token_input = soup.find_all("form")[1].find("input", type="hidden")
        assert token_input is not None
        token = token_input.get("value")
        resp = self._request(
            "https://atcoder.jp/login",
            data={"username": username, "password": password, "csrf_token": token},
            method="POST",
        )

        if resp.text.find("パスワードを忘れた方はこちら") != -1:
            raise LoginError

        if use_local_session_cache and save_session_cache:
            save_cookie(self._session)

    def download_problem_list(self, contest: Contest) -> list[Problem]:
        resp = self._request(contest.get_problem_list_url())
        soup = BeautifulSoup(resp.text, "html.parser")
        res = []
        table = soup.find("table")
        assert table is not None
        for tag in table.select("tr")[1::]:
            a_tag = tag.find("a")
            assert a_tag is not None
            alphabet = a_tag.text
            href = a_tag.get("href")
            assert isinstance(href, str)
            problem_id = href.split("/")[-1]
            res.append(Problem(contest, alphabet, problem_id))
        return res

    def download_problem_content_raw_html(self, problem: Problem) -> str:
        resp = self._request(problem.get_url())
        return resp.text

    def download_problem_content(self, problem: Problem) -> ProblemContent:
        html = self.download_problem_content_raw_html(problem)
        return get_problem_content(html)

    def download_all_contests(self) -> list[Contest]:
        contest_ids = []
        previous_list: list[str] = []
        page_num = 1
        while True:
            resp = self._request(f"https://atcoder.jp/contests/archive?page={page_num}&lang=ja")
            soup = BeautifulSoup(resp.text, "html.parser")
            text = str(soup)
            url_re = re.compile(r'"/contests/([A-Za-z0-9\'~+\-_]+)"')
            contest_set = set(url_re.findall(text))
            contest_set.remove("archive")
            contest_list = sorted(contest_set)

            if previous_list == contest_list:
                break

            previous_list = contest_list
            contest_ids += contest_list
            page_num += 1
        contest_ids = sorted(contest_ids)
        return [Contest(contest_id) for contest_id in contest_ids]

    def submit_source_code(
        self, contest: Contest, problem: Problem, lang: Union[str, Language], source: str
    ) -> Submission:
        lang_option_pattern: Union[str, Pattern[str]]
        if isinstance(lang, str):
            warnings.warn(
                "Parameter lang as a str object is deprecated. "
                "Please use 'atcodertools.common.language.Language' object instead",
                UserWarning,
                stacklevel=2,
            )
            lang_option_pattern = lang
        else:
            lang_option_pattern = lang.submission_lang_pattern

        resp = self._request(contest.get_submit_url())

        soup = BeautifulSoup(resp.text, "html.parser")
        session_input = soup.find("input", attrs={"type": "hidden"})
        assert session_input is not None
        session_id = session_input.get("value")
        task_select_area = soup.find("select", attrs={"id": "select-task"})
        assert task_select_area is not None
        task_select_area.get("name")
        task_option = task_select_area.find("option", string=re.compile(f"{problem.get_alphabet()} -"))
        assert task_option is not None
        task_number = task_option.get("value")
        language_select_area = soup.find("select", attrs={"data-placeholder": "-"})
        assert language_select_area is not None
        language_select_area.get("name")
        language_option = language_select_area.find("option", string=lang_option_pattern)
        assert language_option is not None
        language_number = language_option.get("value")
        postdata = {
            "csrf_token": session_id,
            "data.TaskScreenName": task_number,
            "data.LanguageId": language_number,
            "sourceCode": source,
        }
        resp = self._request(contest.get_submit_url(), data=postdata, method="POST")

        return Submission.make_submissions_from(resp.text)[0]

    def download_submission_list(self, contest: Contest) -> list[Submission]:
        submissions = []
        page_num = 1
        while True:
            resp = self._request(contest.get_my_submissions_url(page_num))
            new_submissions = Submission.make_submissions_from(resp.text)
            if len(new_submissions) == 0:
                break
            submissions += new_submissions
            page_num += 1
        return submissions

    def _request(self, url: str, method: str = "GET", **kwargs: Any) -> requests.Response:
        if method == "GET":
            response = self._session.get(url, **kwargs)
        elif method == "POST":
            response = self._session.post(url, **kwargs)
        else:
            raise NotImplementedError
        response.encoding = response.apparent_encoding
        return response
