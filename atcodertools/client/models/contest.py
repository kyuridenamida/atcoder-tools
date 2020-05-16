from atcodertools.client.models.submission import Submission


class Contest:

    def __init__(self, contest_id):
        self.contest_id = contest_id

    def get_id(self):
        return self.contest_id

    def get_url(self):
        return "https://{}.contest.atcoder.jp/".format(self.contest_id)

    def get_new_url(self):
        return "https://atcoder.jp/contests/{}/".format(self.contest_id)

    def get_problem_list_url(self):
        return "{}assignments".format(self.get_url())

    def get_submit_url(self):
        return "{}submit".format(self.get_new_url())

    def get_my_submissions_url(self, page=1):
        return "{}submissions/me/?page={}".format(self.get_new_url(), page)

    def get_submissions_url(self, submission: Submission):
        return "{}submissions/{}".format(self.get_new_url(), submission.submission_id)

    def to_dict(self):
        return {
            "contest_id": self.contest_id,
        }

    @classmethod
    def from_dict(cls, dic):
        return Contest(contest_id=dic["contest_id"])
