#!/usr/bin/python3

import os
import shutil
import sys
from multiprocessing import Pool, cpu_count
from os.path import expanduser
from time import sleep
from typing import Tuple

from codegen.cpp_code_generator import CppCodeGenerator
from fileutils.create_contest_file import create_examples, create_code_from_prediction_result
from models.problem_content import InputFormatDetectionError, SampleDetectionError
from atcodertools.client.atcoder import AtCoderClient, Contest, LoginError
from atcodertools.fmtprediction.predict_format import FormatPredictor, NoPredictionResultError, \
    MultiplePredictionResultsError
from atcodertools.models.problem import Problem
import logging

fmt = "%(asctime)s %(levelname)s :%(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)


def prepare_procedure(atcoder_client: AtCoderClient,
                      problem: Problem,
                      workspace_root_path: str,
                      successful_template_code_path: str,
                      replacement_code_path: str):
    pid, url = problem.get_alphabet(), problem.get_url()
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

    code_file_path = os.path.join(workspace_dir_path, "main.cpp")

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

        with open(successful_template_code_path, "r") as f:
            template_success = f.read()
        create_code_from_prediction_result(
            result,
            CppCodeGenerator(template_success),
            code_file_path)
        emit_info(
            "Prediction succeeded -- Saved auto-generated code to '{}'".format(code_file_path))
    except (NoPredictionResultError, MultiplePredictionResultsError) as e:
        if isinstance(e, NoPredictionResultError):
            msg = "No prediction -- Failed to understand the input format"
        else:
            msg = "Too many prediction -- Failed to understand the input format"

        emit_warning(
            "{} -- Copied {} to {}".format(
                msg,
                replacement_code_path,
                code_file_path))
        shutil.copy(replacement_code_path, code_file_path)


def func(argv: Tuple[AtCoderClient, Problem, str, str, str]):
    atcoder_client, problem, workspace_root_path, successful_template_code_path, replacement_code_path = argv
    prepare_procedure(
        atcoder_client, problem, workspace_root_path, successful_template_code_path,
                      replacement_code_path)


def prepare_workspace(atcoder_client: AtCoderClient,
                      contest_id: str,
                      workspace_root_path: str,
                      template_code_path: str,
                      replacement_code_path: str,
                      parallel=True
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

    tasks = [(atcoder_client, problem, workspace_root_path, template_code_path, replacement_code_path) for
             problem in problem_list]
    if parallel:
        thread_pool = Pool(processes=cpu_count())
        thread_pool.map(func, tasks)
    else:
        for argv in tasks:
            func(argv)


DEFAULT_WORKSPACE_DIR_PATH = os.path.join(
    expanduser("~"), "atcoder-workspace")
DEFAULT_TEMPLATE_DIR_PATH = "../../templates/cpp/"
DEFAULT_TEMPLATE_PATH = os.path.join(
    DEFAULT_TEMPLATE_DIR_PATH,
     "template_success.cpp")
DEFAULT_REPLACEMENT_PATH = os.path.join(
    DEFAULT_TEMPLATE_DIR_PATH,
     "template_failure.cpp")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("contest_id",
                        help="contest ID (e.g. arc001)")

    parser.add_argument("--without-login",
                        action="store_true",
                        help="download data without login")

    parser.add_argument("--workspace",
                        help="path to workspace's root directory. atc_env will create files"
                             " in {workspace}/(contest name like arc001)/(problem alphabet like A)/",
                        default=DEFAULT_WORKSPACE_DIR_PATH)

    parser.add_argument("--template",
                        help="file path to your template",
                        default=DEFAULT_TEMPLATE_PATH)

    parser.add_argument("--replacement",
                        help="file path to the replacement code created when template generation is failed.",
                        default=DEFAULT_REPLACEMENT_PATH)

    args = parser.parse_args()

    try:
        import AccountInformation
    except ImportError:
        class AccountInformation:
            username = None
            password = None

    client = AtCoderClient()
    if not args.without_login:
        try:
            client.login(
                AccountInformation.username,
                AccountInformation.password)
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
                      args.template,
                      args.replacement)
