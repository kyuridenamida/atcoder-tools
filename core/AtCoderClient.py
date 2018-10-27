import getpass
import http.cookiejar
import re
import urllib.request
from typing import List

from bs4 import BeautifulSoup

from core.models.Contest import Contest
from core.models.Problem import Problem
from core.models.ProblemContent import ProblemContent


class LoginError(Exception):
    pass


class AtCoderClient:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj))

    def login(self, username=None, password=None):
        if username is None:
            username = input('AtCoder username: ')

        if password is None:
            password = getpass.getpass('AtCoder password: ')

        postdata = {
            'name': username,
            'password': password
        }
        encoded_postdata = urllib.parse.urlencode(postdata).encode('utf-8')
        req = self.opener.open(
            "https://arc001.contest.atcoder.jp/login", encoded_postdata)
        html = req.read().decode('utf-8')
        if html.find("パスワードを忘れた方はこちら") != -1:
            raise LoginError

    def download_problem_list(self, contest: Contest) -> List[Problem]:
        req = self.opener.open(contest.get_problem_list_url())
        soup = BeautifulSoup(req, "html.parser")
        res = []
        for tag in soup.select('.linkwrapper')[0::2]:
            alphabet = tag.text
            problem_id = tag.get("href").split("/")[-1]
            res.append(Problem(contest, alphabet, problem_id))
        return res

    def download_problem_content(self, problem: Problem) -> ProblemContent:
        req = self.opener.open(problem.get_url())
        return ProblemContent(req)

    def download_all_contests(self) -> List[Contest]:
        contest_ids = []
        previous_list = []
        page_num = 1
        while True:
            req = self.opener.open(
                "https://atcoder.jp/contest/archive?p={}&lang=ja".format(page_num))
            soup = BeautifulSoup(req, "html.parser")
            text = str(soup)
            url_re = re.compile(
                r'https://([A-Za-z0-9\'~+\-_]+).contest.atcoder.jp')
            contest_list = url_re.findall(text)
            contest_list = sorted(contest_list)

            if previous_list == contest_list:
                break

            previous_list = contest_list
            contest_ids += contest_list
            page_num += 1
        contest_ids = sorted(contest_ids)
        return [Contest(contest_id) for contest_id in contest_ids]

    def submit_source_code(self, contest: Contest, problem: Problem, lang, source):
        req = self.opener.open(contest.submission_url())
        soup = BeautifulSoup(req, "html.parser")
        session_id = soup.find("input", attrs={"type": "hidden"}).get("value")
        task_select_area = soup.find(
            'select', attrs={"id": "submit-task-selector"})
        task_field_name = task_select_area.get("name")
        task_number = task_select_area.find(
            "option", text=re.compile('{} -'.format(problem.get_alphabet()))).get("value")

        language_select_area = soup.find(
            'select', attrs={"id": "submit-language-selector-{}".format(task_number)})
        language_field_name = language_select_area.get("name")
        language_number = language_select_area.find(
            "option", text=re.compile(lang)).get("value")
        postdata = {
            "__session": session_id,
            task_field_name: task_number,
            language_field_name: language_number,
            "source_code": source
        }
        encoded_postdata = urllib.parse.urlencode(postdata).encode('utf-8')
        self.opener.open(contest.get_url(), encoded_postdata) # Sending POST request
