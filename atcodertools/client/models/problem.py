from onlinejudge.service.atcoder import AtCoderContest


class Problem:

    def __init__(self, contest: AtCoderContest, alphabet: str, problem_id: str):
        self.contest = contest
        self.alphabet = alphabet
        self.problem_id = problem_id

    def get_contest(self) -> AtCoderContest:
        return self.contest

    def get_url(self):
        return "{}tasks/{}".format(self.contest.get_url(type='old'), self.problem_id)

    def get_alphabet(self):
        return self.alphabet

    def to_dict(self):
        return {
            "contest": {"contest_id": self.contest.contest_id},
            "problem_id": self.problem_id,
            "alphabet": self.alphabet
        }

    @classmethod
    def from_dict(cls, dic):
        return Problem(
            contest=AtCoderContest(dic["contest"]["contest_id"]),
            problem_id=dic["problem_id"],
            alphabet=dic["alphabet"],
        )
