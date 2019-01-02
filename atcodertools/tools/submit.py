#!/usr/bin/python3
import argparse
import logging
import sys
import os

from atcodertools.client.atcoder import AtCoderClient, LoginError
from atcodertools.tools import tester

from atcodertools.models.tools.metadata import Metadata


def infer_detailed_lang(lang: str):
    if lang == "java":
        return "Java8 (OpenJDK 1.8.0)"
    if lang == "cpp":
        return "C++14 (GCC 5.4.1)"
    raise NotImplementedError


def main(prog, args, credential_supplier=None, use_local_session_cache=True) -> bool:
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--exec", '-e',
                        help="File path to the execution target. [Default] Automatically detected exec file",
                        default=None)

    parser.add_argument("--dir", '-d',
                        help="Target directory to test. [Default] Current directory",
                        default=".")

    parser.add_argument("--timeout", '-t',
                        help="Timeout for each test cases (sec) [Default] 1",
                        type=int,
                        default=1)

    parser.add_argument("--code", '-c',
                        help="Path to the source code to submit [Default] Code path written in metadata.json",
                        type=str,
                        default=None)

    parser.add_argument("--force", "-f",
                        action="store_true",
                        help="Submit the code regardless of the local test result [Default] False",
                        default=False)

    parser.add_argument("--save-no-session-cache",
                        action="store_true",
                        help="Save no session cache to avoid security risk",
                        default=False)

    parser.add_argument("--unlock-safety", "-u",
                        action="store_true",
                        help="By default, this script only submits the first code per problem. However, you can remove"
                             " the safety by this option in order to submit codes twice or more.",
                        default=False)

    args = parser.parse_args(args)

    metadata_file = os.path.join(args.dir, "metadata.json")
    try:
        metadata = Metadata.load_from(metadata_file)
    except IOError:
        logging.error(
            "{0} is not found! You need {0} to use this submission functionality.".format(metadata_file))
        return False

    try:
        client = AtCoderClient()
        client.login(save_session_cache=args.save_no_session_cache,
                     credential_supplier=credential_supplier,
                     use_local_session_cache=use_local_session_cache,
                     )
    except LoginError:
        logging.error("Login failed. Try again.")
        return False

    tester_args = []
    if args.exec:
        tester_args += ["-e", args.exec]
    if args.dir:
        tester_args += ["-d", args.dir]
    if args.timeout:
        tester_args += ["-t", str(args.timeout)]

    if args.force or tester.main("", tester_args):
        submissions = client.download_submission_list(metadata.problem.contest)
        if not args.unlock_safety:
            for submission in submissions:
                if submission.problem_id == metadata.problem.problem_id:
                    logging.error("Cancel submitting because you already sent some code to the problem. Please "
                                  "specify -u to send the code. {}".format(
                                      metadata.problem.contest.get_submissions_url(submission)))
                    return False

        code_path = os.path.join(args.dir, metadata.code_filename)
        with open(code_path, 'r') as f:
            source = f.read()
        detailed_lang = infer_detailed_lang(metadata.lang)
        logging.info("Submitting {} as {}".format(code_path, detailed_lang))
        submission = client.submit_source_code(
            metadata.problem.contest, metadata.problem, detailed_lang, source)
        logging.info("Done! {}".format(
            metadata.problem.contest.get_submissions_url(submission)))


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
