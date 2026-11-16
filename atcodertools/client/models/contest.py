from typing import Any

from atcodertools.client.models.submission import Submission


class Contest:
    def __init__(self, contest_id: str) -> None:
        self.contest_id = contest_id

    def get_id(self) -> str:
        return self.contest_id

    def get_url(self) -> str:
        return f"https://{self.contest_id}.contest.atcoder.jp/"

    def get_new_url(self) -> str:
        return f"https://atcoder.jp/contests/{self.contest_id}/"

    def get_problem_list_url(self) -> str:
        return f"{self.get_url()}assignments"

    def get_submit_url(self) -> str:
        return f"{self.get_new_url()}submit"

    def get_my_submissions_url(self, page: int = 1) -> str:
        return f"{self.get_new_url()}submissions/me/{page}"

    def get_submissions_url(self, submission: Submission) -> str:
        return f"{self.get_new_url()}submissions/{submission.submission_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "contest_id": self.contest_id,
        }

    @classmethod
    def from_dict(cls, dic: dict[str, Any]) -> "Contest":
        return Contest(contest_id=dic["contest_id"])
