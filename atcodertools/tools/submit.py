#!/usr/bin/python3
import argparse
import sys
import os

from colorama import Fore

from atcodertools.tools.tester import USER_FACING_JUDGE_TYPE_LIST, DEFAULT_EPS
from atcodertools.tools.utils import with_color

from atcodertools.client.atcoder import AtCoderClient, LoginError
from atcodertools.tools import tester
from atcodertools.common.logging import logger
from atcodertools.config.config import Config, ConfigType, USER_CONFIG_PATH

from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools import get_default_config_path
from atcodertools.executils.run_command import run_command


def main(prog, args, credential_supplier=None, use_local_session_cache=True, client=None) -> bool:
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

    parser.add_argument('--judge-type', '-j',
                        help='error type'
                             ' must be one of [{}]'.format(
                                 ', '.join(USER_FACING_JUDGE_TYPE_LIST)),
                        type=str,
                        default=None)

    parser.add_argument('--error-value', '-v',
                        help='error value for decimal number judge:'
                             ' [Default] ' + str(DEFAULT_EPS),
                        type=float,
                        default=None)

    parser.add_argument('--exec-before-submit',
                        help='exec command before submit:'
                             ' [Default] None',
                        type=str,
                        default=None)

    parser.add_argument('--exec-after-submit',
                        help='run command after submit:'
                             ' [Default] None',
                        type=str,
                        default=None)

    parser.add_argument('--submit-filename',
                        help='file for submit will changed to this name:'
                             ' [Default] None',
                        type=str,
                        default=None)

    parser.add_argument("--config",
                        help="File path to your config file\n{0}{1}".format("[Default (Primary)] {}\n".format(
                            USER_CONFIG_PATH),
                            "[Default (Secondary)] {}\n".format(
                                get_default_config_path())),
                        type=str,
                        default=None)

    args = parser.parse_args(args)
    if args.config is None:
        if os.path.exists(USER_CONFIG_PATH):
            args.config = USER_CONFIG_PATH
            logger.info(
                f"config is loaded from USER_CONFIG_PATH({USER_CONFIG_PATH})")
        else:
            args.config = get_default_config_path()
            logger.info(
                f"No USER_CONFIG_PATH({USER_CONFIG_PATH}). Default config path({args.config}) is laoded. ")
    metadata_file = os.path.join(args.dir, "metadata.json")

    try:
        metadata = Metadata.load_from(metadata_file)
    except IOError:
        logger.error(
            "{0} is not found! You need {0} to use this submission functionality.".format(metadata_file))
        return False

    with open(args.config, "r") as f:
        config = Config.load(f, {ConfigType.SUBMIT}, args, metadata.lang.name)
    if client is None:
        try:
            client = AtCoderClient()
            client.login(save_session_cache=not args.save_no_session_cache,
                         credential_supplier=credential_supplier,
                         use_local_session_cache=use_local_session_cache,
                         )
        except LoginError:
            logger.error("Login failed. Try again.")
            return False

    tester_args = []
    if args.exec:
        tester_args += ["-e", args.exec]
    if args.dir:
        tester_args += ["-d", args.dir]
    if args.timeout:
        tester_args += ["-t", str(args.timeout)]
    if args.judge_type is not None:
        tester_args += ["-j", str(args.judge_type)]
    if args.error_value is not None:
        tester_args += ["-v", str(args.error_value)]

    if args.force or tester.main("", tester_args):
        if not args.unlock_safety:
            submissions = client.download_submission_list(
                metadata.problem.contest)
            for submission in submissions:
                if submission.problem_id == metadata.problem.problem_id:
                    logger.error(with_color("Cancel submitting because you already sent some code to the problem. Please "
                                            "specify -u to send the code. {}".format(
                                                metadata.problem.contest.get_submissions_url(submission)), Fore.LIGHTRED_EX))
                    return False

        code_path = args.code or os.path.join(args.dir, metadata.code_filename)

        if config.submit_config.exec_before_submit:
            run_command(config.submit_config.exec_before_submit, args.dir)
            if not config.submit_config.submit_filename:
                logger.error("submit_filename is not specified")
                return False
            code_path = config.submit_config.submit_filename
            logger.info(f"changed to submitfile: {code_path}")

        for encoding in ['utf8', 'utf-8_sig', 'cp932']:
            try:
                with open(os.path.join(args.dir, code_path), 'r', encoding=encoding) as f:
                    source = f.read()
                break
            except UnicodeDecodeError:
                logger.warning("code wasn't recognized as {}".format(encoding))
        logger.info(
            "Submitting {} as {}".format(code_path, metadata.lang.name))
        submission = client.submit_source_code(
            metadata.problem.contest, metadata.problem, metadata.lang, source)
        logger.info("{} {}".format(
            with_color("Done!", Fore.LIGHTGREEN_EX),
            metadata.problem.contest.get_submissions_url(submission)))
        if config.submit_config.exec_after_submit:
            run_command(config.submit_config.exec_after_submit, args.dir)

    return True


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
