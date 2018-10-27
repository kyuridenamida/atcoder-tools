from core.utils import normalized, pure_japanese_text
import getpass
import re
import urllib.request
from collections import OrderedDict
from bs4 import BeautifulSoup
from typing import List, Set, Dict, Tuple, Optional

import http.cookiejar


class LoginError(Exception):
    pass


class SampleParseError(Exception):
    pass


class InputParseError(Exception):
    pass


class Contest:
    def __init__(self, contest_id):
        self.contest_id = contest_id

    def get_id(self):
        return self.contest_id

    def get_url(self):
        return "http://{}.contest.atcoder.jp/".format(self.contest_id)

    def get_problem_list_url(self):
        return "{}assignments".format(self.get_url())

    def submission_url(self):
        return "{}submit".format(self.get_url())

class Problem:
    def __init__(self, contest, alphabet, problem_id):
        self.contest = contest
        self.alphabet = alphabet
        self.problem_id = problem_id

    def get_contest(self) -> Contest:
        return self.contest

    def get_url(self):
        return "{}tasks/{}".format(self.contest.get_url(), self.problem_id)

    def get_alphabet(self):
        return self.alphabet


class Sample:
    def __init__(self, input_text, output_text):
        self.input_text = input_text
        self.output_text = output_text

    def get_output(self):
        return self.output_text

    def get_input(self):
        return self.input_text


class ProblemContent:
    input_format_text = None
    samples = None

    def get_input_format(self) -> str:
        return self.input_format_text

    def get_samples(self) -> List[Sample]:
        return self.samples

    def __init__(self, req):
        self.soup = BeautifulSoup(req, "html.parser")
        self.remove_english_statements()
        self.focus_on_atcoder_format()
        self.input_format_text, self.samples = self.extract_input_format_and_samples()

    def remove_english_statements(self):
        for e in self.soup.findAll("span", {"class": "lang-en"}):
            e.extract()

    def focus_on_atcoder_format(self):
        # Preferably use atCoder format
        tmp = self.soup.select('.part')
        if tmp:
            tmp[0].extract()

    def extract_input_format_and_samples(self) -> Tuple[str, List[Sample]]:
        try:
            input_format_tag, input_tags, output_tags = self.prior_strategy()
            if input_format_tag is None:
                raise InputParseError
        except InputParseError:
            input_format_tag, input_tags, output_tags = self.alternative_strategy()

        if len(input_tags) != len(output_tags):
            raise SampleParseError

        res = [Sample(normalized(in_tag.text), normalized(out_tag.text))
               for in_tag, out_tag in zip(input_tags, output_tags)]

        if input_format_tag is None:
            raise InputParseError

        input_format_text = normalized(input_format_tag.text)

        return input_format_text, res

    def prior_strategy(self):  # TODO: more descriptive name
        input_tags = []
        output_tags = []
        input_format_tag = None
        for tag in self.soup.select('section'):
            h3tag = tag.find('h3')
            if h3tag is None:
                continue
            # Some problem has strange characters in h3 tags which should be removed
            section_title = pure_japanese_text(tag.find('h3').get_text())

            if section_title.startswith("入力例"):
                input_tags.append(tag.find('pre'))
            elif section_title.startswith("入力"):
                input_format_tag = tag.find('pre')

            if section_title.startswith("出力例"):
                output_tags.append(tag.find('pre'))
        return input_format_tag, input_tags, output_tags

    def alternative_strategy(self):  # TODO: more descriptive name
        pre_tags = self.soup.select('pre')
        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tag = pre_tags[0]
        return input_format_tag, input_tags, output_tags


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
