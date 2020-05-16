import getpass
import os
import re
import warnings
from http.cookiejar import LWPCookieJar
from typing import List, Optional, Tuple, Union

import requests
from bs4 import BeautifulSoup

from atcodertools.client.models.contest import Contest
from atcodertools.client.models.problem import Problem
from atcodertools.client.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError
from atcodertools.client.models.submission import Submission
from atcodertools.common.language import Language
from atcodertools.common.logging import logger
from atcodertools.fileutils.artifacts_cache import get_cache_file_path


class LoginError(Exception):
    pass


class PageNotFoundError(Exception):
    pass


default_cookie_path = get_cache_file_path('cookie.txt')


def save_cookie(session: requests.Session, cookie_path: Optional[str] = None):
    cookie_path = cookie_path or default_cookie_path
    os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
    session.cookies.save()
    logger.info("Saved session into {}".format(os.path.abspath(cookie_path)))
    os.chmod(cookie_path, 0o600)


def load_cookie_to(session: requests.Session, cookie_path: Optional[str] = None):
    cookie_path = cookie_path or default_cookie_path
    session.cookies = LWPCookieJar(cookie_path)
    if os.path.exists(cookie_path):
        session.cookies.load()
        logger.info(
            "Loaded session from {}".format(os.path.abspath(cookie_path)))
        return True
    return False


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def default_credential_supplier() -> Tuple[str, str]:
    username = input('AtCoder username: ')
    password = getpass.getpass('AtCoder password: ')
    return username, password


class AtCoderClient(metaclass=Singleton):

    def __init__(self):
        self._session = requests.Session()

    def check_logging_in(self):
        private_url = "https://atcoder.jp/home"
        resp = self._request(private_url)
        return resp.text.find("Sign In") == -1

    def login(self,
              credential_supplier=None,
              use_local_session_cache=True,
              save_session_cache=True):

        if credential_supplier is None:
            credential_supplier = default_credential_supplier

        if use_local_session_cache:
            load_cookie_to(self._session)
            if self.check_logging_in():
                logger.info(
                    "Successfully Logged in using the previous session cache.")
                logger.info(
                    "If you'd like to invalidate the cache, delete {}.".format(default_cookie_path))

                return

        username, password = credential_supplier()

        soup = BeautifulSoup(self._session.get(
            "https://atcoder.jp/login").text, "html.parser")
        token = soup.find_all("form")[1].find(
            "input", type="hidden").get("value")
        resp = self._request("https://atcoder.jp/login", data={
            'username': username,
            "password": password,
            "csrf_token": token
        }, method='POST')

        if resp.text.find("パスワードを忘れた方はこちら") != -1:
            raise LoginError

        if use_local_session_cache and save_session_cache:
            save_cookie(self._session)

    def download_problem_list(self, contest: Contest) -> List[Problem]:
        resp = self._request(contest.get_problem_list_url())
        soup = BeautifulSoup(resp.text, "html.parser")
        if resp.status_code == 404:
            raise PageNotFoundError
        res = []
        for tag in soup.find('table').select('tr')[1::]:
            tag = tag.find("a")
            alphabet = tag.text
            problem_id = tag.get("href").split("/")[-1]
            res.append(Problem(contest, alphabet, problem_id))
        return res

    def download_problem_content(self, problem: Problem) -> ProblemContent:
        resp = self._request(problem.get_url())

        try:
            return ProblemContent.from_html(resp.text)
        except (InputFormatDetectionError, SampleDetectionError) as e:
            raise e

    def download_all_contests(self) -> List[Contest]:
        contest_ids = []
        previous_list = []
        page_num = 1
        while True:
            resp = self._request(
                "https://atcoder.jp/contests/archive?page={}&lang=ja".format(page_num))
            soup = BeautifulSoup(resp.text, "html.parser")
            text = str(soup)
            url_re = re.compile(
                r'"/contests/([A-Za-z0-9\'~+\-_]+)"')
            contest_list = url_re.findall(text)
            contest_list = set(contest_list)
            contest_list.remove("archive")
            contest_list = sorted(list(contest_list))

            if previous_list == contest_list:
                break

            previous_list = contest_list
            contest_ids += contest_list
            page_num += 1
        contest_ids = sorted(contest_ids)
        return [Contest(contest_id) for contest_id in contest_ids]

    def submit_source_code(self, contest: Contest, problem: Problem, lang: Union[str, Language], source: str) -> Submission:
        if isinstance(lang, str):
            warnings.warn(
                "Parameter lang as a str object is deprecated. "
                "Please use 'atcodertools.common.language.Language' object instead",
                UserWarning)
            lang_option_pattern = lang
        else:
            lang_option_pattern = lang.submission_lang_pattern

        resp = self._request(contest.get_submit_url())

        soup = BeautifulSoup(resp.text, "html.parser")
        session_id = soup.find("input", attrs={"type": "hidden"}).get("value")
        task_select_area = soup.find(
            'select', attrs={"id": "select-task"})
        task_number = task_select_area.find(
            "option", text=re.compile('{} -'.format(problem.get_alphabet()))).get("value")
        language_select_area = soup.find(
            'select', attrs={"data-placeholder": "-"})
        language_number = language_select_area.find(
            "option", text=lang_option_pattern).get("value")
        postdata = {
            "csrf_token": session_id,
            "data.TaskScreenName": task_number,
            "data.LanguageId": language_number,
            "sourceCode": source
        }
        resp = self._request(
            contest.get_submit_url(),
            data=postdata,
            method='POST')

        return Submission.make_submissions_from(resp.text)[0]

    def download_submission_list(self, contest: Contest) -> List[Submission]:
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

    def _request(self, url: str, method='GET', **kwargs):
        if method == 'GET':
            response = self._session.get(url, **kwargs)
        elif method == 'POST':
            response = self._session.post(url, **kwargs)
        else:
            raise NotImplementedError
        response.encoding = response.apparent_encoding
        return response
