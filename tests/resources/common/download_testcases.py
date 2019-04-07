#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import os

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.client.models.problem_content import SampleDetectionError, InputFormatDetectionError


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
        try:
            problems = atcoder.download_problem_list(contest)
        except Exception as e:
            print("Failed to download {}. {}".format(contest.contest_id, e))
            print("Skipping ...")

        for problem in problems:
            path = "./test_data/{contest}-{problem_id}".format(contest=contest.contest_id,
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
            except SampleDetectionError:
                print(
                    "failed to parse samples for {} {} -- skipping download".format(contest.contest_id,
                                                                                    problem.get_alphabet()))
            except InputFormatDetectionError:
                print(
                    "failed to parse input for {} {} -- skipping download".format(contest.contest_id,
                                                                                  problem.get_alphabet()))
            except Exception:
                print("unknown error for {} {} -- skipping download".format(
                    contest.contest_id, problem.get_alphabet()))
