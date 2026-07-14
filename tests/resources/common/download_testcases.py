#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import os

from atcodertools.client.atcoder import (
    AtCoderClient,
)
from atcodertools.client.models.problem_content import (
    InputFormatDetectionError,
    SampleDetectionError,
)
from tests.utils.problem_content_fixture import (
    CONTENT_FILE_NAME,
    write_problem_content_fixture,
)


atcoder = AtCoderClient()


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as error:
        if not (
            error.errno == errno.EEXIST
            and os.path.isdir(path)
        ):
            raise


def write_legacy_files(path, content):
    with open(
        os.path.join(path, "format.txt"),
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            content.get_input_format()
        )

    for index, sample in enumerate(
        content.get_samples(),
        start=1,
    ):
        with open(
            os.path.join(
                path,
                "ex_{}.txt".format(index),
            ),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(
                sample.get_input()
            )


def save_problem(path, contest, problem):
    content_path = os.path.join(
        path,
        CONTENT_FILE_NAME,
    )

    if os.path.exists(content_path):
        print(
            "{} already exists -- "
            "skipping download".format(
                content_path
            )
        )
        return

    content = atcoder.download_problem_content(
        problem
    )
    mkdirs(path)

    write_problem_content_fixture(
        path,
        content,
        source={
            "contest_id": contest.get_id(),
            "problem_alphabet": (
                problem.get_alphabet()
            ),
        },
    )
    write_legacy_files(path, content)


if __name__ == "__main__":
    for contest in (
        atcoder.download_all_contests()
    ):
        for problem in (
            atcoder.download_problem_list(
                contest
            )
        ):
            path = (
                "./test_data/"
                "{contest}-{problem_id}"
            ).format(
                contest=contest.get_id(),
                problem_id=(
                    problem.get_alphabet()
                ),
            )

            try:
                save_problem(
                    path,
                    contest,
                    problem,
                )
            except SampleDetectionError:
                print(
                    "failed to parse samples "
                    "for {} {} -- "
                    "skipping download".format(
                        contest.get_id(),
                        problem.get_alphabet(),
                    )
                )
            except InputFormatDetectionError:
                print(
                    "failed to parse input "
                    "for {} {} -- "
                    "skipping download".format(
                        contest.get_id(),
                        problem.get_alphabet(),
                    )
                )
            except Exception as error:
                print(
                    "unknown error for {} {}: "
                    "{} -- skipping "
                    "download".format(
                        contest.get_id(),
                        problem.get_alphabet(),
                        error,
                    )
                )
