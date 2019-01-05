#!/usr/bin/python3
import argparse
import os
import shutil
import sys
from multiprocessing import Pool, cpu_count
from os.path import expanduser
from time import sleep
from typing import Tuple, Optional

from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.codegen.java_code_generator import JavaCodeGenerator
from atcodertools.config.config import Config
from atcodertools.fileutils.create_contest_file import create_examples, create_code_from
from atcodertools.constprediction.constants_prediction import predict_constants
from atcodertools.fileutils.create_contest_file import create_examples, \
    create_code_from
from atcodertools.models.problem_content import InputFormatDetectionError, SampleDetectionError
from atcodertools.client.atcoder import AtCoderClient, Contest, LoginError
from atcodertools.fmtprediction.predict_format import FormatPredictor, NoPredictionResultError, \
    MultiplePredictionResultsError
from atcodertools.models.problem import Problem
import logging

from atcodertools.models.tools.metadata import Metadata

script_dir_path = os.path.dirname(os.path.abspath(__file__))

fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)


class BannedFileDetectedError(Exception):
    pass


def extension(lang: str):
    return lang


IN_EXAMPLE_FORMAT = "in_{}.txt"
OUT_EXAMPLE_FORMAT = "out_{}.txt"


def output_splitter():
    # for readability
    print("=================================================", file=sys.stderr)


def _message_on_execution(cwd: str, cmd: str):
    return "Executing the following command in `{}`: {}".format(cwd, cmd)


def prepare_procedure(atcoder_client: AtCoderClient,
                      problem: Problem,
                      workspace_root_path: str,
                      template_code_path: str,
                      replacement_code_path: str,
                      lang: str,
                      config: Config,
                      ):
    pid = problem.get_alphabet()
    problem_dir_path = os.path.join(
        workspace_root_path,
        problem.get_contest().get_id(),
        pid)

    def emit_error(text):
        logging.error("Problem {}: {}".format(pid, text))

    def emit_warning(text):
        logging.warning("Problem {}: {}".format(pid, text))

    def emit_info(text):
        logging.info("Problem {}: {}".format(pid, text))

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
                        IN_EXAMPLE_FORMAT, OUT_EXAMPLE_FORMAT)
        emit_info("Created examples.")

    code_file_path = os.path.join(
        problem_dir_path,
        "main.{}".format(extension(lang)))

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
        if lang == "cpp":
            gen_class = CppCodeGenerator
        elif lang == "java":
            gen_class = JavaCodeGenerator
        else:
            raise NotImplementedError("only supporting cpp and java")

        with open(template_code_path, "r") as f:
            template = f.read()

        result = FormatPredictor().predict(content)
        constants = predict_constants(content.original_html)

        create_code_from(
            result,
            constants,
            gen_class(template, config.code_style_config),
            code_file_path)
        emit_info(
            "Prediction succeeded -- Saved auto-generated code to '{}'".format(code_file_path))
    except (NoPredictionResultError, MultiplePredictionResultsError) as e:
        if isinstance(e, NoPredictionResultError):
            msg = "No prediction -- Failed to understand the input format"
        else:
            msg = "Too many prediction -- Failed to understand the input format"

        os.makedirs(os.path.dirname(code_file_path), exist_ok=True)
        shutil.copy(replacement_code_path, code_file_path)
        emit_warning(
            "{} -- Copied {} to {}".format(
                msg,
                replacement_code_path,
                code_file_path))

    # Save metadata
    metadata_path = os.path.join(problem_dir_path, "metadata.json")
    Metadata(problem,
             os.path.basename(code_file_path),
             IN_EXAMPLE_FORMAT.replace("{}", "*"),
             OUT_EXAMPLE_FORMAT.replace("{}", "*"),
             lang,
             ).save_to(metadata_path)
    emit_info("Saved metadata to {}".format(metadata_path))

    if config.postprocess_config.exec_cmd_on_problem_dir is not None:
        emit_info(_message_on_execution(problem_dir_path,
                                        config.postprocess_config.exec_cmd_on_problem_dir))
        config.postprocess_config.execute_on_problem_dir(
            problem_dir_path)

    output_splitter()


def func(argv: Tuple[AtCoderClient, Problem, str, str, str, str, Config]):
    atcoder_client, problem, workspace_root_path, template_code_path, replacement_code_path, lang, config = argv
    prepare_procedure(
        atcoder_client, problem, workspace_root_path, template_code_path,
        replacement_code_path, lang, config)


def prepare_contest(atcoder_client: AtCoderClient,
                    contest_id: str,
                    workspace_root_path: str,
                    template_code_path: str,
                    replacement_code_path: str,
                    lang: str,
                    parallel: bool,
                    config: Config,
                    ):
    retry_duration = 1.5
    while True:
        problem_list = atcoder_client.download_problem_list(
            Contest(contest_id=contest_id))
        if problem_list:
            break
        sleep(retry_duration)
        logging.warning(
            "Failed to fetch. Will retry in {} seconds".format(retry_duration))

    tasks = [(atcoder_client, problem, workspace_root_path, template_code_path, replacement_code_path, lang, config) for
             problem in problem_list]

    output_splitter()

    if parallel:
        thread_pool = Pool(processes=cpu_count())
        thread_pool.map(func, tasks)
    else:
        for argv in tasks:
            func(argv)

    if config.postprocess_config.exec_cmd_on_contest_dir is not None:
        contest_dir_path = os.path.join(workspace_root_path, contest_id)
        logging.info(_message_on_execution(contest_dir_path,
                                           config.postprocess_config.exec_cmd_on_contest_dir))
        config.postprocess_config.execute_on_contest_dir(
            contest_dir_path)


DEFAULT_WORKSPACE_DIR_PATH = os.path.join(
    expanduser("~"), "atcoder-workspace")

DEFAULT_TEMPLATE_DIR_PATH = os.path.abspath(
    os.path.join(script_dir_path, "./templates/"))


def get_default_template_path(lang):
    return os.path.abspath(os.path.join(DEFAULT_TEMPLATE_DIR_PATH, "{lang}/template_success.{lang}".format(lang=lang)))


def get_default_replacement_path(lang):
    return os.path.abspath(os.path.join(DEFAULT_TEMPLATE_DIR_PATH, "{lang}/template_failure.{lang}").format(lang=lang))


DEFAULT_LANG = "cpp"
SUPPORTED_LANGUAGES = ["cpp", "java"]


def check_lang(lang: str):
    lang = lang.lower()
    if lang not in SUPPORTED_LANGUAGES:
        raise argparse.ArgumentTypeError("{} is not supported. The available languages are {}"
                                         .format(lang, SUPPORTED_LANGUAGES))
    return lang


USER_CONFIG_PATH = os.path.join(
    expanduser("~"), ".atcodertools.toml")
DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(script_dir_path, "./atcodertools-default.toml"))


def get_config(config_path: Optional[str] = None) -> Config:
    def _load(path: str) -> Config:
        logging.info("Going to load {} as config".format(path))
        with open(path, 'r') as f:
            return Config.load(f)

    if config_path:
        return _load(config_path)

    if os.path.exists(USER_CONFIG_PATH):
        return _load(USER_CONFIG_PATH)

    return _load(DEFAULT_CONFIG_PATH)


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
                             "[Default] {}".format(DEFAULT_WORKSPACE_DIR_PATH),
                        default=DEFAULT_WORKSPACE_DIR_PATH)

    parser.add_argument("--lang",
                        help="Programming language of your template code, {}.\n"
                        .format(" or ".join(SUPPORTED_LANGUAGES)) + "[Default] {}".format(DEFAULT_LANG),
                        default=DEFAULT_LANG,
                        type=check_lang)

    parser.add_argument("--template",
                        help="File path to your template code\n{0}{1}".format(
                            "[Default (C++)] {}\n".format(
                                get_default_template_path('cpp')),
                            "[Default (Java)] {}".format(
                                get_default_template_path('java')))
                        )

    parser.add_argument("--replacement",
                        help="File path to your config file\n{0}{1}".format(
                            "[Default (C++)] {}\n".format(get_default_replacement_path('cpp')),
                            "[Default (Java)] {}".format(
                                get_default_replacement_path('java')))
                        )

    parser.add_argument("--parallel",
                        action="store_true",
                        help="Prepare problem directories asynchronously using multi processors.",
                        default=False)

    parser.add_argument("--save-no-session-cache",
                        action="store_true",
                        help="Save no session cache to avoid security risk",
                        default=False)

    parser.add_argument("--config",
                        help="File path to your config file\n{0}{1}".format("[Default (Primary)] {}\n".format(
                            USER_CONFIG_PATH),
                            "[Default (Secondary)] {}\n".format(
                                DEFAULT_CONFIG_PATH))
                        )

    args = parser.parse_args(args)

    try:
        import AccountInformation  # noqa
        raise BannedFileDetectedError(
            "We abolished the logic with AccountInformation.py. Please delete the file.")
    except ImportError:
        pass

    client = AtCoderClient()
    if not args.without_login:
        try:
            client.login(save_session_cache=not args.save_no_session_cache)
            logging.info("Login successful.")
        except LoginError:
            logging.error(
                "Failed to login (maybe due to wrong username/password combination?)")
            sys.exit(-1)
    else:
        logging.info("Downloading data without login.")

    prepare_contest(client,
                    args.contest_id,
                    args.workspace,
                    args.template if args.template is not None else get_default_template_path(
                        args.lang),
                    args.replacement if args.replacement is not None else get_default_replacement_path(
                        args.lang),
                    args.lang,
                    args.parallel,
                    get_config(args.config)
                    )


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
