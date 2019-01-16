from argparse import Namespace
from typing import TextIO, Dict, Any, Optional

import toml

from atcodertools.config.code_style_config import CodeStyleConfig
from atcodertools.config.etc_config import EtcConfig
from atcodertools.config.postprocess_config import PostprocessConfig


def merge_dict(org_dic: Dict[str, Any], dic: Dict[str, Any]):
    for k, v in dic.items():
        if v is not None:
            org_dic[k] = v

    return org_dic


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
            code_style_config_dic = merge_dict(code_style_config_dic, {
                "template_file": args.template,
                "workspace_dir": args.workspace,
                "lang": args.lang,
            })
            etc_config_dic = merge_dict(etc_config_dic, {
                "without_login": args.without_login,
                "parallel": args.parallel,
                "save_no_session_cache": args.save_no_session_cache,
            })

        return Config(
            code_style_config=CodeStyleConfig(**code_style_config_dic),
            postprocess_config=PostprocessConfig(**postprocess_config_dic),
            etc_config=EtcConfig(**etc_config_dic)
        )
