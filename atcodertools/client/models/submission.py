import re

from bs4 import BeautifulSoup

PROB_URL_RE = re.compile(
    r'"/contests/.*/tasks/([A-Za-z0-9\'~+\-_]+)"')
SUBMISSION_URL_RE = re.compile(
    r'/submissions/([0-9]+)')


class Submission:

    def __init__(self, problem_id: str, submission_id: int):
        self.problem_id = problem_id
        self.submission_id = submission_id

    @staticmethod
    def make_submissions_from(html: str):
        soup = BeautifulSoup(html, "html.parser")
        text = str(soup)
        submitted_problem_ids = PROB_URL_RE.findall(text)
        submission_ids = SUBMISSION_URL_RE.findall(text)
        assert len(submitted_problem_ids) == len(submission_ids)
        return [Submission(pid, int(sid)) for pid, sid in zip(submitted_problem_ids, submission_ids)]
