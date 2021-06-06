from argparse import Namespace
from typing import TextIO, Dict, Any, Optional

import toml
import os
from os.path import expanduser
import argparse
from atcodertools.common.logging import logger

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.config.etc_config import EtcConfig
from atcodertools.config.postprocess_config import PostprocessConfig
from atcodertools.tools import get_default_config_path


def _update_config_dict(target_dic: Dict[str, Any], update_dic: Dict[str, Any]):
    return {
        **target_dic,
        **dict((k, v) for k, v in update_dic.items() if v is not None)
    }


class Config:

    def __init__(self,
                 code_style_config: CodeStyleConfig = CodeStyleConfig(),
                 postprocess_config: PostprocessConfig = PostprocessConfig(),
                 etc_config: EtcConfig = EtcConfig()
                 ):
        self.code_style_config = code_style_config
        self.postprocess_config = postprocess_config
        self.etc_config = etc_config

    @classmethod
    def load(cls, fp: TextIO, args: Optional[Namespace] = None):
        """
        :param fp: .toml file's file pointer
        :param args: command line arguments
        :return: Config instance
        """
        config_dic = toml.load(fp)

        code_style_config_dic = config_dic.get('codestyle', {})
        postprocess_config_dic = config_dic.get('postprocess', {})
        etc_config_dic = config_dic.get('etc', {})

        if args:
            code_style_config_dic = _update_config_dict(code_style_config_dic,
                                                        dict(
                                                            template_file=args.template,
                                                            workspace_dir=args.workspace,
                                                            lang=args.lang))
            etc_config_dic = _update_config_dict(etc_config_dic,
                                                 dict(
                                                     download_without_login=args.without_login,
                                                     parallel_download=args.parallel,
                                                     save_no_session_cache=args.save_no_session_cache,
                                                     skip_existing_problems=args.skip_existing_problems))

        return Config(
            code_style_config=CodeStyleConfig(**code_style_config_dic),
            postprocess_config=PostprocessConfig(**postprocess_config_dic),
            etc_config=EtcConfig(**etc_config_dic)
        )


USER_CONFIG_PATH = os.path.join(
    expanduser("~"), ".atcodertools.toml")


def get_config(args: argparse.Namespace) -> Config:
    def _load(path: str) -> Config:
        logger.info("Going to load {} as config".format(path))
        with open(path, 'r') as f:
#            program_args = ProgramArgs.load(args)
#
#            if language is not None:
#                assert program_args.lang is None
#                program_args.lang = language.name

            return Config.load(f)

    if args.config:
        return _load(args.config)

    if os.path.exists(USER_CONFIG_PATH):
        return _load(USER_CONFIG_PATH)

    return _load(get_default_config_path())
