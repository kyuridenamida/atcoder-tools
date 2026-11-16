from typing import Any, Dict

from atcodertools.client.models.submission import Submission


class Contest:

    def __init__(self, contest_id: str) -> None:
        self.contest_id = contest_id

    def get_id(self) -> str:
        return self.contest_id

    def get_url(self) -> str:
        return "https://{}.contest.atcoder.jp/".format(self.contest_id)

    def get_new_url(self) -> str:
        return "https://atcoder.jp/contests/{}/".format(self.contest_id)

    def get_problem_list_url(self) -> str:
        return "{}assignments".format(self.get_url())

    def get_submit_url(self) -> str:
        return "{}submit".format(self.get_new_url())

    def get_my_submissions_url(self, page: int = 1) -> str:
        return "{}submissions/me/{}".format(self.get_new_url(), page)

    def get_submissions_url(self, submission: Submission) -> str:
        return "{}submissions/{}".format(self.get_new_url(), submission.submission_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contest_id": self.contest_id,
        }

    @classmethod
    def from_dict(cls, dic: Dict[str, Any]) -> "Contest":
        return Contest(contest_id=dic["contest_id"])
