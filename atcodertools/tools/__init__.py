import pathlib


def get_default_config_path() -> str:
    return str(pathlib.Path(__file__).parent / "atcodertools-default.toml")
