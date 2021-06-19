from argparse import Namespace
from typing import TextIO, Dict, Any, Optional
from enum import Enum

import toml

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.config.etc_config import EtcConfig
from atcodertools.config.postprocess_config import PostprocessConfig
from atcodertools.config.tester_config import TesterConfig


class ConfigType(Enum):
    CODESTYLE = "codestyle"
    POSTPROCESS = "postprocess"
    TESTER = "tester"
    ETC = "etc"


def _update_config_dict(target_dic: Dict[str, Any], update_dic: Dict[str, Any]):
    return {
        **target_dic,
        **dict((k, v) for k, v in update_dic.items() if v is not None)
    }


def get_config_dic(config_dic, config_type: ConfigType, lang=None):
    result = dict()
    d = config_dic.get(config_type.value, {})
    lang_dic = {}
    for k, v in d.items():
        if type(v) is dict:
            if k == lang:
                lang_dic = v
        else:
            result[k] = v
    result = _update_config_dict(result, lang_dic)
    return result


class Config:

    def __init__(self,
                 code_style_config: CodeStyleConfig = CodeStyleConfig(),
                 postprocess_config: PostprocessConfig = PostprocessConfig(),
                 tester_config: TesterConfig = TesterConfig(),
                 etc_config: EtcConfig = EtcConfig()
                 ):
        self.code_style_config = code_style_config
        self.postprocess_config = postprocess_config
        self.tester_config = tester_config
        self.etc_config = etc_config

    @classmethod
    def load(cls, fp: TextIO, get_config_type, args: Optional[Namespace] = None, lang=None):
        """
        :param fp: .toml file's file pointer
        :param args: command line arguments
        :return: Config instance
        """
        config_dic = toml.load(fp)

        result = Config()
        if not lang:
            if args and args.lang:
                lang = args.lang
            elif "codestyle" in config_dic:
                lang = config_dic["codestyle"].get("lang", None)

        if ConfigType.CODESTYLE in get_config_type:
            code_style_config_dic = get_config_dic(
                config_dic, ConfigType.CODESTYLE, lang)
            if args:
                code_style_config_dic = _update_config_dict(code_style_config_dic,
                                                            dict(
                                                                template_file=args.template,
                                                                workspace_dir=args.workspace,
                                                                lang=lang))
            result.code_style_config = CodeStyleConfig(**code_style_config_dic)
        if ConfigType.POSTPROCESS in get_config_type:
            postprocess_config_dic = get_config_dic(
                config_dic, ConfigType.POSTPROCESS)
            result.postprocess_config = PostprocessConfig(
                **postprocess_config_dic)
        if ConfigType.TESTER in get_config_type:
            tester_config_dic = get_config_dic(
                config_dic, ConfigType.TESTER, lang)
            if args:
                tester_config_dic = _update_config_dict(tester_config_dic,
                                                        dict(compile_before_testing=args.compile_before_testing,
                                                             compile_only_when_diff_detected=args.compile_only_when_diff_detected,
                                                             compile_command=args.compile_command))
            result.tester_config = TesterConfig(**tester_config_dic)
        if ConfigType.ETC in get_config_type:
            etc_config_dic = get_config_dic(config_dic, ConfigType.ETC)
            if args:
                etc_config_dic = _update_config_dict(etc_config_dic,
                                                     dict(
                                                         download_without_login=args.without_login,
                                                         parallel_download=args.parallel,
                                                         save_no_session_cache=args.save_no_session_cache,
                                                         skip_existing_problems=args.skip_existing_problems))
            result.etc_config = EtcConfig(**etc_config_dic)

        return result
