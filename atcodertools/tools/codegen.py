#!/usr/bin/python3
import argparse
import sys
from io import IOBase

from colorama import Fore
from onlinejudge.service.atcoder import AtCoderProblem

from atcodertools.client.atcoder import AtCoderClient, LoginError
from atcodertools.client.models.problem_content import InputFormatDetectionError, SampleDetectionError
from atcodertools.codegen.code_style_config import DEFAULT_WORKSPACE_DIR_PATH
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.common.language import ALL_LANGUAGES, CPP
from atcodertools.common.logging import logger
from atcodertools.config.config import Config
from atcodertools.constprediction.constants_prediction import predict_constants
from atcodertools.fmtprediction.models.format_prediction_result import FormatPredictionResult
from atcodertools.fmtprediction.predict_format import MultiplePredictionResultsError, NoPredictionResultError, predict_format
from atcodertools.tools import get_default_config_path
from atcodertools.tools.envgen import USER_CONFIG_PATH, get_config, output_splitter
from atcodertools.tools.utils import with_color


class UnknownProblemURLError(Exception):
    pass


def generate_code(atcoder_client: AtCoderClient,
                  problem_url: str,
                  config: Config,
                  output_file: IOBase):
    problem = AtCoderProblem.from_url(problem_url)
    if problem is None:
        raise UnknownProblemURLError
    template_code_path = config.code_style_config.template_file

    def emit_error(text):
        logger.error(with_color(text, Fore.RED))

    def emit_warning(text):
        logger.warning(text)

    def emit_info(text):
        logger.info(text)

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

    constants = predict_constants(content)
    code_generator = config.code_style_config.code_generator
    with open(template_code_path, "r") as f:
        template = f.read()

    output_splitter()

    output_file.write(code_generator(
        CodeGenArgs(
            template,
            prediction_result.format,
            constants,
            config.code_style_config
        )))


def main(prog, args, output_file=sys.stdout):
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("url",
                        help="URL (e.g. https://atcoder.jp/contests/abc012/tasks/abc012_3)")

    parser.add_argument("--without-login",
                        action="store_true",
                        help="Download data without login")

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

    parser.add_argument("--save-no-session-cache",
                        action="store_true",
                        help="Save no session cache to avoid security risk",
                        default=None)

    parser.add_argument("--config",
                        help="File path to your config file\n{0}{1}".format("[Default (Primary)] {}\n".format(
                            USER_CONFIG_PATH),
                            "[Default (Secondary)] {}\n".format(
                                get_default_config_path()))
                        )

    args = parser.parse_args(args)

    args.workspace = DEFAULT_WORKSPACE_DIR_PATH  # dummy for get_config()
    args.parallel = False  # dummy for get_config()
    config = get_config(args)

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

    generate_code(client,
                  args.url,
                  config,
                  output_file=output_file)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
