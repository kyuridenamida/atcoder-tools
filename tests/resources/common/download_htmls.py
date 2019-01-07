#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import os

from atcodertools.client.atcoder import AtCoderClient


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
    htmls_dir = "./problem_htmls/"
    mkdirs(htmls_dir)
    for contest in atcoder.download_all_contests():
        for problem in atcoder.download_problem_list(contest):
            html_path = os.path.join(htmls_dir, "{contest}-{problem_id}.html".format(
                contest=contest.get_id(), problem_id=problem.get_alphabet()))

            if os.path.exists(html_path):
                print(
                    "{} already exists -- skipping download".format(html_path))
                continue

            print("Downloading {}".format(html_path))
            try:
                html = atcoder.download_problem_content(problem).original_html
                with open(html_path, 'w') as f:
                    f.write(html)
            except Exception as e:
                print("Failed to download {}. {}".format(html_path, e))
                print("Skipping ...")
