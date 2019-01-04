from typing import TextIO

import toml

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.tools.postprocess_config import PostprocessConfig


class Config:
    def __init__(self,
                 code_style_config: CodeStyleConfig = CodeStyleConfig(),
                 postprocess_config: PostprocessConfig = PostprocessConfig(),
                 ):
        self.code_style_config = code_style_config
        self.postprocess_config = postprocess_config

    @classmethod
    def load(cls, fp: TextIO):
        config_dic = toml.load(fp)
        code_style_config_dic = config_dic.get('codestyle', {})
        postprocess_config_dic = config_dic.get('postprocess', {})
        return Config(
            code_style_config=CodeStyleConfig(**code_style_config_dic),
            postprocess_config=PostprocessConfig(
                exec_cmd_for_problem=postprocess_config_dic.get(
                    "exec_foreach_problem", None),
                exec_cmd_for_contest=postprocess_config_dic.get(
                    "exec_for_contest", None),
            ))
