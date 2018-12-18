#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import os

from core.client.AtCoderClient import AtCoderClient
from core.models.ProblemContent import SampleParseError, InputParseError


class NoPatternFoundError(Exception):
    pass


atcoder = AtCoderClient()


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass


if __name__ == "__main__":
    for contest in atcoder.download_all_contests():
        for problem in atcoder.download_problem_list(contest):
            path = "./test_data/{contest}-{problem_id}".format(contest=contest.get_id(),
                                                               problem_id=problem.get_alphabet())
            if os.path.exists(path) and len(os.listdir(path)) != 0:
                print("{} already exists -- skipping download".format(path))
                continue

            try:
                content = atcoder.download_problem_content(problem)

                mkdirs(path)
                with open("{}/{}".format(path, "format.txt"), "w") as f:
                    f.write(content.get_input_format())

                for idx, sample in enumerate(content.get_samples()):
                    with open("{}/ex_{}.txt".format(path, idx + 1), "w") as f:
                        f.write(sample.get_input())
            except SampleParseError as e:
                print("failed to parse samples for {} {} -- skipping download".format(contest.get_id(),
                                                                                      problem.get_alphabet()))
            except InputParseError as e:
                print("failed to parse input for {} {} -- skipping download".format(contest.get_id(),
                                                                                    problem.get_alphabet()))
            except Exception as e:
                print("unknown error for {} {} -- skipping download".format(contest.get_id(), problem.get_alphabet()))
