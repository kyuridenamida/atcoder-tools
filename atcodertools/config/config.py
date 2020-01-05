from typing import TextIO, Dict, Any, Optional

import os
import argparse
from os.path import expanduser
import toml
from colorama import Fore

from atcodertools.common.language import Language
from atcodertools.common.logging import logger

from atcodertools.codegen.code_style_config import CodeStyleConfig, DEFAULT_LANGUAGE
from atcodertools.config.etc_config import EtcConfig
from atcodertools.config.postprocess_config import PostprocessConfig
from atcodertools.config.run_config import RunConfig
from atcodertools.tools import get_default_config_path
from atcodertools.tools.utils import with_color

_POST_PROCESS_CONFIG_KEY = "postprocess"

_CODE_STYLE_CONFIG_KEY = "codestyle"

_RUN_CONFIG_KEY = "run"


class ProgramArgs:
    def __init__(
            self,
            template: Optional[str] = None,
            workspace: Optional[str] = None,
            without_login: Optional[bool] = None,
            parallel: Optional[bool] = None,
            save_no_session_cache: Optional[bool] = None,
            lang: Optional[str] = None,
            compile_before_testing: Optional[bool] = None,
            compile_only_when_diff_detected: Optional[bool] = None
    ):
        self.template = template
        self.workspace = workspace
        self.without_login = without_login
        self.parallel = parallel
        self.save_no_session_cache = save_no_session_cache
        self.lang = lang
        self.compile_before_testing = compile_before_testing
        self.compile_only_when_diff_detected = compile_only_when_diff_detected

    @classmethod
    def load(cls, program_args: argparse.Namespace):
        return ProgramArgs(
            **{k: v for k, v in program_args.__dict__.items() if k in (
                "template",
                "workspace",
                "without_login",
                "parallel",
                "save_no_session_cache",
                "lang",
                "compile_before_testing",
                "compile_only_when_diff_detected"
            )})


def _update_config_dict(target_dic: Dict[str, Any], update_dic: Dict[str, Any]):
    return {
        **target_dic,
        **dict((k, v) for k, v in update_dic.items() if v is not None)
    }


class Config:

    def __init__(self,
                 code_style_config: CodeStyleConfig = CodeStyleConfig(),
                 postprocess_config: PostprocessConfig = PostprocessConfig(),
                 etc_config: EtcConfig = EtcConfig(),
                 run_config: RunConfig = RunConfig()
                 ):
        self.code_style_config = code_style_config
        self.postprocess_config = postprocess_config
        self.etc_config = etc_config
        self.run_config = run_config

    @classmethod
    def load(cls, fp: TextIO, args: Optional[ProgramArgs] = None):
        """
        :param fp: .toml file's file pointer
        :param args: command line arguments
        :return: Config instance
        """
        config_dic = toml.load(fp)
        # Root 'codestyle' is common code style
        common_code_style_config_dic = config_dic.get(
            _CODE_STYLE_CONFIG_KEY, {})

        postprocess_config_dic = config_dic.get(_POST_PROCESS_CONFIG_KEY, {})
        etc_config_dic = config_dic.get('etc', {})
        run_config_dic = config_dic.get(_RUN_CONFIG_KEY, {})
        code_style_config_dic = {**common_code_style_config_dic}

        # Handle config override strategy in the following code
        # (Most preferred) program arguments > lang-specific > common config (Least preferred)
        lang = (args and args.lang) or common_code_style_config_dic.get(
            "lang", DEFAULT_LANGUAGE)
        code_style_config_dic = _update_config_dict(
            code_style_config_dic, dict(lang=lang))

        if lang in config_dic:
            lang_specific_config_dic = config_dic[lang]  # e.g. [cpp.codestyle]
            if _CODE_STYLE_CONFIG_KEY in lang_specific_config_dic:
                lang_code_style = lang_specific_config_dic[_CODE_STYLE_CONFIG_KEY]
                if "lang" in lang_code_style:
                    logger.warn(
                        with_color("'lang' is only valid in common code style config, "
                                   "but detected in language-specific code style config. It will be ignored.",
                                   Fore.RED))
                    del lang_code_style["lang"]

                code_style_config_dic = _update_config_dict(code_style_config_dic,
                                                            lang_code_style)

            # e.g. [cpp.postprocess]
            if _POST_PROCESS_CONFIG_KEY in lang_specific_config_dic:
                postprocess_config_dic = _update_config_dict(postprocess_config_dic,
                                                             lang_specific_config_dic[_POST_PROCESS_CONFIG_KEY])

            if _RUN_CONFIG_KEY in lang_specific_config_dic:  # e.g. [cpp.run]
                run_config_dic = _update_config_dict(run_config_dic,
                                                     lang_specific_config_dic[_RUN_CONFIG_KEY])

        if args:
            code_style_config_dic = _update_config_dict(
                code_style_config_dic,
                dict(template_file=args.template,
                     workspace_dir=args.workspace)
            )
            etc_config_dic = _update_config_dict(
                etc_config_dic,
                dict(
                    download_without_login=args.without_login,
                    parallel_download=args.parallel,
                    save_no_session_cache=args.save_no_session_cache,
                    compile_before_testing=args.compile_before_testing,
                    compile_only_when_diff_detected=args.compile_only_when_diff_detected
                )
            )

        return Config(
            code_style_config=CodeStyleConfig(**code_style_config_dic),
            postprocess_config=PostprocessConfig(**postprocess_config_dic),
            etc_config=EtcConfig(**etc_config_dic),
            run_config=RunConfig(**run_config_dic)
        )


USER_CONFIG_PATH = os.path.join(
    expanduser("~"), ".atcodertools.toml")


def get_config(args: argparse.Namespace, language: Language = None) -> Config:
    def _load(path: str) -> Config:
        logger.info("Going to load {} as config".format(path))
        with open(path, 'r') as f:
            program_args = ProgramArgs.load(args)

            if language is not None:
                assert program_args.lang is None
                program_args.lang = language.name

            return Config.load(f, program_args)

    if args.config:
        return _load(args.config)

    if os.path.exists(USER_CONFIG_PATH):
        return _load(USER_CONFIG_PATH)

    return _load(get_default_config_path())
