import os


def get_default_config_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "atcodertools-default.toml")
