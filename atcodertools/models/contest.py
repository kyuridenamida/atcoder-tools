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
