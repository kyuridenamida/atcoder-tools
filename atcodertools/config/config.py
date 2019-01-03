from typing import TextIO

import toml

from atcodertools.codegen.codegen_config import CodeGenConfig
from atcodertools.tools.envgen_config import EnvGenConfig


class ConfigInitError(Exception):
    pass


class Config:
    def __init__(self,
                 code_gen_config: CodeGenConfig = CodeGenConfig(),
                 env_gen_config: EnvGenConfig = EnvGenConfig(),
                 ):
        self.code_gen_config = code_gen_config
        self.env_gen_config = env_gen_config

    @classmethod
    def load(cls, fp: TextIO):
        config_dic = toml.load(fp)
        code_gen_config_dic = config_dic.get('codestyle', {})
        env_gen_config_dic = config_dic.get('postprocess', {})
        return Config(
            code_gen_config=CodeGenConfig(**code_gen_config_dic),
            env_gen_config=EnvGenConfig(**env_gen_config_dic)
        )
