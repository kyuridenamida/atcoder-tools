from atcodertools.models.contest import Contest


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
