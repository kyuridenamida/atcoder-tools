from atcodertools.client.models.contest import Contest


class Problem:

    def __init__(self, contest: Contest, alphabet: str, problem_id: str):
        self.contest = contest
        self.alphabet = alphabet
        self.problem_id = problem_id

    def get_contest(self) -> Contest:
        return self.contest

    def get_url(self):
        return "{}tasks/{}".format(self.contest.get_url(), self.problem_id)

    def get_alphabet(self):
        return self.alphabet

    def to_dict(self):
        return {
            "contest": self.contest.to_dict(),
            "problem_id": self.problem_id,
            "alphabet": self.alphabet
        }

    @classmethod
    def from_dict(cls, dic):
        return Problem(
            contest=Contest.from_dict(dic["contest"]),
            problem_id=dic["problem_id"],
            alphabet=dic["alphabet"],
        )
