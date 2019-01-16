import os


def get_default_config_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "atcodertools-default.toml")
