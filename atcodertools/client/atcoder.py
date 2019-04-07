import getpass
import logging
import os
import re
import warnings
from http.cookiejar import LWPCookieJar
from typing import List, Optional, Tuple, Union

import requests
from bs4 import BeautifulSoup
from onlinejudge.type import Submission, LoginError
from onlinejudge.service.atcoder import AtCoderService, AtCoderContest, AtCoderProblem

from atcodertools.client.models.sample import Sample
from atcodertools.common.language import Language
from atcodertools.fileutils.artifacts_cache import get_cache_file_path
from atcodertools.client.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError


default_cookie_path = get_cache_file_path('cookie.txt')


def save_cookie(session: requests.Session, cookie_path: Optional[str] = None):
    cookie_path = cookie_path or default_cookie_path
    os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
    session.cookies.save()
    logging.info("Saved session into {}".format(os.path.abspath(cookie_path)))
    os.chmod(cookie_path, 0o600)


def load_cookie_to(session: requests.Session, cookie_path: Optional[str] = None):
    cookie_path = cookie_path or default_cookie_path
    session.cookies = LWPCookieJar(cookie_path)
    if os.path.exists(cookie_path):
        session.cookies.load()
        logging.info(
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
        return AtCoderService().is_logged_in(session=self._session)

    def login(self,
              credential_supplier=None,
              use_local_session_cache=True,
              save_session_cache=True):

        if credential_supplier is None:
            credential_supplier = default_credential_supplier

        if use_local_session_cache:
            load_cookie_to(self._session)
            if self.check_logging_in():
                logging.info(
                    "Successfully Logged in using the previous session cache.")
                logging.info(
                    "If you'd like to invalidate the cache, delete {}.".format(default_cookie_path))

                return

        AtCoderService().login(credential_supplier, session=self._session)

        if use_local_session_cache and save_session_cache:
            save_cookie(self._session)

    def download_problem_list(self, contest: AtCoderContest) -> List[AtCoderProblem]:
        return contest.list_problems(session=self._session)

    def download_problem_content(self, problem: AtCoderProblem) -> ProblemContent:
        content = problem.download_content(session=self._session)
        return ProblemContent.from_raw_content(content)

    def download_all_contests(self) -> List[AtCoderContest]:
        return list(AtCoderService().iterate_contests(
            session=self._session))

    def submit_source_code(self, contest: AtCoderContest, problem: AtCoderProblem, lang: Union[str, Language], source: str) -> Submission:
        if isinstance(lang, str):
            warnings.warn(
                "Parameter lang as a str object is deprecated. "
                "Please use 'atcodertools.common.language.Language' object instead",
                UserWarning)
            lang_option_pattern = lang
        else:
            lang_option_pattern = lang.submission_lang_pattern

        for available_language in problem.get_available_languages(session=self._session):
            if re.match(lang_option_pattern, available_language.name):
                language_id = available_language.id
                break
        else:
            raise Exception(
                'failed to recognize the language: {}'.format(lang))
        return problem.submit_code(
            source.encode(), language_id=language_id, session=self._session)

    def download_submission_list(self, contest: AtCoderContest) -> List[Submission]:
        return list(contest.iterate_submissions_where(me=True, session=self._session))

    def _request(self, url: str, method='GET', **kwargs):
        if method == 'GET':
            response = self._session.get(url, **kwargs)
        elif method == 'POST':
            response = self._session.post(url, **kwargs)
        else:
            raise NotImplementedError
        response.encoding = response.apparent_encoding
        return response
