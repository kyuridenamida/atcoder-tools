#!/usr/bin/python3
import argparse
import os
import shutil
import sys
from multiprocessing import Pool, cpu_count
from os.path import expanduser
from time import sleep
from typing import Tuple

from atcodertools.codegen.cpp_code_generator import CppCodeGenerator
from atcodertools.codegen.java_code_generator import JavaCodeGenerator
from atcodertools.fileutils.create_contest_file import create_examples, create_code_from_prediction_result
from atcodertools.models.problem_content import InputFormatDetectionError, SampleDetectionError
from atcodertools.client.atcoder import AtCoderClient, Contest, LoginError
from atcodertools.fmtprediction.predict_format import FormatPredictor, NoPredictionResultError, \
    MultiplePredictionResultsError
from atcodertools.models.problem import Problem
import logging

script_dir_path = os.path.dirname(os.path.abspath(__file__))

fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)


class BannedFileDetectedError(Exception):
    pass


def extension(lang: str):
    return lang


def prepare_procedure(atcoder_client: AtCoderClient,
                      problem: Problem,
                      workspace_root_path: str,
                      template_code_path: str,
                      replacement_code_path: str,
                      lang: str):
    pid = problem.get_alphabet()
    workspace_dir_path = os.path.join(
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
        os.makedirs(workspace_dir_path, exist_ok=True)
        create_examples(content.get_samples(), workspace_dir_path)
        emit_info("Created examples.")

    code_file_path = os.path.join(
        workspace_dir_path,
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
        result = FormatPredictor().predict(content)

        with open(template_code_path, "r") as f:
            template = f.read()

        if lang == "cpp":
            gen_class = CppCodeGenerator
        elif lang == "java":
            gen_class = JavaCodeGenerator
        else:
            raise NotImplementedError("only supporting cpp and java")

        create_code_from_prediction_result(
            result,
            gen_class(template),
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


def func(argv: Tuple[AtCoderClient, Problem, str, str, str, str]):
    atcoder_client, problem, workspace_root_path, template_code_path, replacement_code_path, lang = argv
    prepare_procedure(
        atcoder_client, problem, workspace_root_path, template_code_path,
        replacement_code_path, lang)


def prepare_workspace(atcoder_client: AtCoderClient,
                      contest_id: str,
                      workspace_root_path: str,
                      template_code_path: str,
                      replacement_code_path: str,
                      lang: str,
                      parallel: bool):
    retry_duration = 1.5
    while True:
        problem_list = atcoder_client.download_problem_list(
            Contest(contest_id=contest_id))
        if problem_list:
            break
        sleep(retry_duration)
        logging.warning(
            "Failed to fetch. Will retry in {} seconds".format(retry_duration))

    tasks = [(atcoder_client, problem, workspace_root_path, template_code_path, replacement_code_path, lang) for
             problem in problem_list]
    if parallel:
        thread_pool = Pool(processes=cpu_count())
        thread_pool.map(func, tasks)
    else:
        for argv in tasks:
            func(argv)


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


def main(prog, args):
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("contest_id",
                        help="contest ID (e.g. arc001)")

    parser.add_argument("--without-login",
                        action="store_true",
                        help="download data without login")

    parser.add_argument("--workspace",
                        help="path to workspace's root directory. This script will create files"
                             " in {{WORKSPACE}}/{{contest_name}}/{{alphabet}}/ e.g. ./your-workspace/arc001/A/\n"
                             "[Default] {}".format(DEFAULT_WORKSPACE_DIR_PATH),
                        default=DEFAULT_WORKSPACE_DIR_PATH)

    parser.add_argument("--lang",
                        help="programming language of your template code, {}.\n"
                        .format(" or ".join(SUPPORTED_LANGUAGES)) + "[Default] {}".format(DEFAULT_LANG),
                        default=DEFAULT_LANG,
                        type=check_lang)

    parser.add_argument("--template",
                        help="{0}{1}".format("file path to your template code\n"
                                             "[Default (C++)] {}\n".format(
                                                 get_default_template_path('cpp')),
                                             "[Default (Java)] {}".format(
                                                 get_default_template_path('java')))
                        )

    parser.add_argument("--replacement",
                        help="{0}{1}".format(
                            "file path to the replacement code created when template generation is failed.\n"
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

    prepare_workspace(client,
                      args.contest_id,
                      args.workspace,
                      args.template if args.template is not None else get_default_template_path(
                          args.lang),
                      args.replacement if args.replacement is not None else get_default_replacement_path(
                          args.lang),
                      args.lang,
                      args.parallel)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
