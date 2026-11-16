#!/usr/bin/python3
import argparse
import os
import sys
from typing import Callable, Optional

from colorama import Fore

from atcodertools.client.atcoder import AtCoderClient, LoginError
from atcodertools.common.logging import logger
from atcodertools.tools import tester
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.tester import DEFAULT_EPS, USER_FACING_JUDGE_TYPE_LIST
from atcodertools.tools.utils import with_color


def main(
    prog: str,
    args: list[str],
    credential_supplier: Optional[Callable[[], tuple[str, str]]] = None,
    use_local_session_cache: bool = True,
) -> bool:
    parser = argparse.ArgumentParser(prog=prog, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "--exec",
        "-e",
        help="File path to the execution target. [Default] Automatically detected exec file",
        default=None,
    )

    parser.add_argument("--dir", "-d", help="Target directory to test. [Default] Current directory", default=".")

    parser.add_argument("--timeout", "-t", help="Timeout for each test cases (sec) [Default] 1", type=int, default=1)

    parser.add_argument(
        "--code",
        "-c",
        help="Path to the source code to submit [Default] Code path written in metadata.json",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Submit the code regardless of the local test result [Default] False",
        default=False,
    )

    parser.add_argument(
        "--save-no-session-cache",
        action="store_true",
        help="Save no session cache to avoid security risk",
        default=False,
    )

    parser.add_argument(
        "--unlock-safety",
        "-u",
        action="store_true",
        help="By default, this script only submits the first code per problem. However, you can remove"
        " the safety by this option in order to submit codes twice or more.",
        default=False,
    )

    parser.add_argument(
        "--judge-type",
        "-j",
        help="error type must be one of [{}]".format(", ".join(USER_FACING_JUDGE_TYPE_LIST)),
        type=str,
        default=None,
    )

    parser.add_argument(
        "--error-value",
        "-v",
        help="error value for decimal number judge: [Default] " + str(DEFAULT_EPS),
        type=float,
        default=None,
    )

    parsed_args = parser.parse_args(args)

    metadata_file = os.path.join(parsed_args.dir, "metadata.json")
    try:
        metadata = Metadata.load_from(metadata_file)
    except OSError:
        logger.error(f"{metadata_file} is not found! You need {metadata_file} to use this submission functionality.")
        return False

    try:
        client = AtCoderClient()
        client.login(
            save_session_cache=not parsed_args.save_no_session_cache,
            credential_supplier=credential_supplier,
            use_local_session_cache=use_local_session_cache,
        )
    except LoginError:
        logger.error("Login failed. Try again.")
        return False

    tester_args = []
    if parsed_args.exec:
        tester_args += ["-e", parsed_args.exec]
    if parsed_args.dir:
        tester_args += ["-d", parsed_args.dir]
    if parsed_args.timeout:
        tester_args += ["-t", str(parsed_args.timeout)]
    if parsed_args.judge_type is not None:
        tester_args += ["-j", str(parsed_args.judge_type)]
    if parsed_args.error_value is not None:
        tester_args += ["-v", str(parsed_args.error_value)]

    if parsed_args.force or tester.main("", tester_args):
        assert metadata.problem is not None and metadata.lang is not None
        submissions = client.download_submission_list(metadata.problem.contest)
        if not parsed_args.unlock_safety:
            for submission in submissions:
                if submission.problem_id == metadata.problem.problem_id:
                    logger.error(
                        with_color(
                            "Cancel submitting because you already sent some code to the problem. Please "
                            f"specify -u to send the code. {metadata.problem.contest.get_submissions_url(submission)}",
                            Fore.LIGHTRED_EX,
                        )
                    )
                    return False

        assert metadata.code_filename is not None
        code_path = parsed_args.code or os.path.join(parsed_args.dir, metadata.code_filename)
        with open(code_path) as f:
            source = f.read()
        logger.info(f"Submitting {code_path} as {metadata.lang.name}")
        submission = client.submit_source_code(metadata.problem.contest, metadata.problem, metadata.lang, source)
        logger.info(
            "{} {}".format(
                with_color("Done!", Fore.LIGHTGREEN_EX), metadata.problem.contest.get_submissions_url(submission)
            )
        )
        return True
    return False


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
