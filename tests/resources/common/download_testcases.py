#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import os
import time

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
        if contest.get_id().startswith("asprocon") or contest.get_id().startswith("future-meets-you-contest"):
            continue
        try:
            d = atcoder.download_problem_list(contest)
        except Exception:
            print("download problem list error for {}".format(contest.get_id()))
            time.sleep(120)
            continue
        for problem in d:
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
            except SampleDetectionError:
                print(
                    "failed to parse samples for {} {} -- skipping download".format(contest.get_id(),
                                                                                    problem.get_alphabet()))
            except InputFormatDetectionError:
                print(
                    "failed to parse input for {} {} -- skipping download".format(contest.get_id(),
                                                                                  problem.get_alphabet()))
            except Exception:
                print("unknown error for {} {} -- skipping download".format(
                    contest.get_id(), problem.get_alphabet()))
