import unittest

from atcodertools.client.atcoder import AtCoderClient, LoginError
from atcodertools.models.contest import Contest
from atcodertools.models.problem import Problem

ANSWER_FILE = "./resources/test_fmtprediction/answer.txt"


class TestAtCoderClient(unittest.TestCase):

    def setUp(self):
        self.client = AtCoderClient()

    def test_download_problem_list(self):
        problem_list = self.client.download_problem_list(Contest("arc002"))
        self.assertEqual(
            ['arc002_1',
             'arc002_2',
             'arc002_3',
             'arc002_4'],
            [p.problem_id for p in problem_list])

    def test_download_problem_content(self):
        content = self.client.download_problem_content(
            Problem(Contest("arc002"), "C", "arc002_3"))
        self.assertEqual("N\nc_{1}c_{2}...c_{N}\n", content.input_format_text)
        self.assertEqual(3, len(content.samples))
        # return ProblemContent(req)

    def test_login_failed(self):
        try:
            self.client.login(
                username="@@@ invalid user name @@@",
                password="@@@@@@@")
            self.fail("Unexpectedly, this test succeeded to login.")
        except LoginError:
            pass

    def test_download_all_contests(self):
        contests = self.client.download_all_contests()
        # Check if the number of contests is more than the number when I wrote
        # this unit test.
        self.assertGreaterEqual(len(contests), 523)

        # Make sure there is no duplication
        self.assertEqual(
            len(set([c.get_id() for c in contests])),
            len(contests))


if __name__ == "__main__":
    unittest.main()
