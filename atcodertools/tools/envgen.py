#!/usr/bin/python3
import argparse
import os
import shutil
import sys
import traceback
from multiprocessing import Pool, cpu_count
from os.path import expanduser
import time
from typing import Tuple

from colorama import Fore

from atcodertools.client.atcoder import AtCoderClient, Contest, LoginError, PageNotFoundError
from atcodertools.client.models.problem import Problem
from atcodertools.client.models.problem_content import InputFormatDetectionError, SampleDetectionError
from atcodertools.codegen.code_style_config import DEFAULT_WORKSPACE_DIR_PATH
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.common.language import ALL_LANGUAGES, CPP
from atcodertools.common.logging import logger
from atcodertools.config.config import Config
from atcodertools.constprediction.constants_prediction import predict_constants
from atcodertools.fileutils.create_contest_file import create_examples, \
    create_code
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult
from atcodertools.fmtprediction.predict_format import NoPredictionResultError, \
    MultiplePredictionResultsError, predict_format
from atcodertools.tools import get_default_config_path
from atcodertools.tools.models.metadata import Metadata
from atcodertools.tools.utils import with_color


class BannedFileDetectedError(Exception):
    pass


class EnvironmentInitializationError(Exception):
    pass


def output_splitter():
    # for readability
    print("=================================================", file=sys.stderr)


def _message_on_execution(cwd: str, cmd: str):
    return "Executing the following command in `{}`: {}".format(cwd, cmd)


def prepare_procedure(atcoder_client: AtCoderClient,
                      problem: Problem,
                      config: Config):
    workspace_root_path = config.code_style_config.workspace_dir
    template_code_path = config.code_style_config.template_file
    lang = config.code_style_config.lang

    pid = problem.get_alphabet()
    problem_dir_path = os.path.join(
        workspace_root_path,
        problem.get_contest().get_id(),
        pid)

    def emit_error(text):
        logger.error(with_color("Problem {}: {}".format(pid, text), Fore.RED))

    def emit_warning(text):
        logger.warning("Problem {}: {}".format(pid, text))

    def emit_info(text):
        logger.info("Problem {}: {}".format(pid, text))

    # Return if a directory for the problem already exists
    if config.etc_config.skip_existing_problems:
        if os.path.exists(problem_dir_path):
            emit_info(
                f"Skipped preparation because the directory already exists: {problem_dir_path}")
            return

    emit_info('{} is used for template'.format(template_code_path))

    # Fetch problem data from the statement
    try:
        content = atcoder_client.download_problem_content(problem)
    except InputFormatDetectionError as e:
        emit_error("Failed to download input format.")
        raise e
    except SampleDetectionError as e:
        emit_error("Failed to download samples.")
        raise e

    # Store examples to the directory path
    if len(content.get_samples()) == 0:
        emit_info("No samples.")
    else:
        os.makedirs(problem_dir_path, exist_ok=True)
        create_examples(content.get_samples(), problem_dir_path,
                        config.etc_config.in_example_format, config.etc_config.out_example_format)
        emit_info("Created examples.")

    code_file_path = os.path.join(
        problem_dir_path,
        "main.{}".format(lang.extension))

    # If there is an existing code, just create backup
    if os.path.exists(code_file_path):
        backup_id = 1
        while True:
            backup_name = "{}.{}".format(code_file_path, backup_id)
            if not os.path.exists(backup_name):
                new_path = backup_name
                shutil.copy(code_file_path, backup_name)
                break
            backup_id += 1
        emit_info(
            "Backup for existing code '{}' -> '{}'".format(
                code_file_path,
                new_path))

    try:
        prediction_result = predict_format(content)
        emit_info(
            with_color("Format prediction succeeded", Fore.LIGHTGREEN_EX))
    except (NoPredictionResultError, MultiplePredictionResultsError) as e:
        prediction_result = FormatPredictionResult.empty_result()
        if isinstance(e, NoPredictionResultError):
            msg = "No prediction -- Failed to understand the input format"
        else:
            msg = "Too many prediction -- Failed to understand the input format"
        emit_warning(with_color(msg, Fore.LIGHTRED_EX))

    constants = predict_constants(content.original_html)
    code_generator = config.code_style_config.code_generator
    with open(template_code_path, "r") as f:
        template = f.read()

    create_code(code_generator(
        CodeGenArgs(
            template,
            prediction_result.format,
            constants,
            config.code_style_config
        )),
        code_file_path)
    emit_info("Saved code to {}".format(code_file_path))

    # Save metadata
    metadata_path = os.path.join(problem_dir_path, "metadata.json")
    Metadata(problem,
             os.path.basename(code_file_path),
             config.etc_config.in_example_format.replace("{}", "*"),
             config.etc_config.out_example_format.replace("{}", "*"),
             lang,
             constants.judge_method,
             ).save_to(metadata_path)
    emit_info("Saved metadata to {}".format(metadata_path))

    if config.postprocess_config.exec_cmd_on_problem_dir is not None:
        emit_info(_message_on_execution(problem_dir_path,
                                        config.postprocess_config.exec_cmd_on_problem_dir))
        config.postprocess_config.execute_on_problem_dir(
            problem_dir_path)

    output_splitter()


def func(argv: Tuple[AtCoderClient, Problem, Config]):
    atcoder_client, problem, config = argv
    prepare_procedure(atcoder_client, problem, config)


def prepare_contest(atcoder_client: AtCoderClient,
                    contest_id: str,
                    config: Config,
                    retry_delay_secs: float = 1.5,
                    retry_max_delay_secs: float = 60,
                    retry_max_tries: int = 10):
    attempt_count = 1
    while True:
        try:
            problem_list = atcoder_client.download_problem_list(
                Contest(contest_id=contest_id))
            break
        except PageNotFoundError:
            if 0 < retry_max_tries < attempt_count:
                raise EnvironmentInitializationError
            logger.warning(
                "Failed to fetch. Will retry in {} seconds. (Attempt {})".format(retry_delay_secs, attempt_count))
            time.sleep(retry_delay_secs)
            retry_delay_secs = min(retry_delay_secs * 2, retry_max_delay_secs)
            attempt_count += 1

    tasks = [(atcoder_client,
              problem,
              config) for
             problem in problem_list]

    output_splitter()

    if config.etc_config.parallel_download:
        thread_pool = Pool(processes=cpu_count())
        thread_pool.map(func, tasks)
    else:
        for argv in tasks:
            try:
                func(argv)
            except Exception:
                # Prevent the script from stopping
                print(traceback.format_exc(), file=sys.stderr)
                pass

    if config.postprocess_config.exec_cmd_on_contest_dir is not None:
        contest_dir_path = os.path.join(
            config.code_style_config.workspace_dir, contest_id)
        logger.info(_message_on_execution(contest_dir_path,
                                          config.postprocess_config.exec_cmd_on_contest_dir))
        config.postprocess_config.execute_on_contest_dir(
            contest_dir_path)


USER_CONFIG_PATH = os.path.join(
    expanduser("~"), ".atcodertools.toml")


def get_config(args: argparse.Namespace) -> Config:
    def _load(path: str) -> Config:
        logger.info("Going to load {} as config".format(path))
        with open(path, 'r') as f:
            return Config.load(f, args)

    if args.config:
        return _load(args.config)

    if os.path.exists(USER_CONFIG_PATH):
        return _load(USER_CONFIG_PATH)

    return _load(get_default_config_path())


class DeletedFunctionalityError(Exception):
    pass


def main(prog, args):
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("contest_id",
                        help="Contest ID (e.g. arc001)")

    parser.add_argument("--without-login",
                        action="store_true",
                        help="Download data without login")

    parser.add_argument("--workspace",
                        help="Path to workspace's root directory. This script will create files"
                             " in {{WORKSPACE}}/{{contest_name}}/{{alphabet}}/ e.g. ./your-workspace/arc001/A/\n"
                             "[Default] {}".format(DEFAULT_WORKSPACE_DIR_PATH))

    parser.add_argument("--lang",
                        help="Programming language of your template code, {}.\n"
                        .format(" or ".join([lang.name for lang in ALL_LANGUAGES])) + "[Default] {}".format(CPP.name))

    parser.add_argument("--template",
                        help="File path to your template code\n{}".format(
                            "\n".join(
                                ["[Default ({dname})] {path}".format(
                                    dname=lang.display_name,
                                    path=lang.default_template_path
                                ) for lang in ALL_LANGUAGES]
                            ))
                        )

    # Deleted functionality
    parser.add_argument('--replacement', help=argparse.SUPPRESS)

    parser.add_argument("--parallel",
                        action="store_true",
                        help="Prepare problem directories asynchronously using multi processors.",
                        default=None)

    parser.add_argument("--save-no-session-cache",
                        action="store_true",
                        help="Save no session cache to avoid security risk",
                        default=None)

    parser.add_argument("--skip-existing-problems",
                        action="store_true",
                        help="Skip processing every problem for which a directory already exists",
                        default=None)

    parser.add_argument("--config",
                        help="File path to your config file\n{0}{1}".format("[Default (Primary)] {}\n".format(
                            USER_CONFIG_PATH),
                            "[Default (Secondary)] {}\n".format(
                                get_default_config_path()))
                        )

    args = parser.parse_args(args)

    if args.replacement is not None:
        logger.error(with_color("Sorry! --replacement argument no longer exists"
                                " and you can only use --template."
                                " See the official document for details.", Fore.LIGHTRED_EX))
        raise DeletedFunctionalityError

    config = get_config(args)

    try:
        import AccountInformation  # noqa
        raise BannedFileDetectedError(
            "We abolished the logic with AccountInformation.py. Please delete the file.")
    except ImportError:
        pass

    client = AtCoderClient()
    if not config.etc_config.download_without_login:
        try:
            client.login(
                save_session_cache=not config.etc_config.save_no_session_cache)
            logger.info("Login successful.")
        except LoginError:
            logger.error(
                "Failed to login (maybe due to wrong username/password combination?)")
            sys.exit(-1)
    else:
        logger.info("Downloading data without login.")

    prepare_contest(client,
                    args.contest_id,
                    config)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
