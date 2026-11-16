from typing import Any

from atcodertools.client.models.contest import Contest


class Problem:
    def __init__(self, contest: Contest, alphabet: str, problem_id: str) -> None:
        self.contest = contest
        self.alphabet = alphabet
        self.problem_id = problem_id

    def get_contest(self) -> Contest:
        return self.contest

    def get_url(self) -> str:
        return f"{self.contest.get_url()}tasks/{self.problem_id}"

    def get_alphabet(self) -> str:
        return self.alphabet

    def to_dict(self) -> dict[str, Any]:
        return {"contest": self.contest.to_dict(), "problem_id": self.problem_id, "alphabet": self.alphabet}

    @classmethod
    def from_dict(cls, dic: dict[str, Any]) -> "Problem":
        return Problem(
            contest=Contest.from_dict(dic["contest"]),
            problem_id=dic["problem_id"],
            alphabet=dic["alphabet"],
        )
