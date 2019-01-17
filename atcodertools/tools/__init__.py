import pathlib


def get_default_config_path():
    return pathlib.Path(pathlib.Path(__file__).parent, "atcodertools-default.toml").resolve()
