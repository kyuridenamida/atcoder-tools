import pathlib

DEFAULT_TEMPLATE_DIR_PATH = pathlib.Path(__file__).parent


def get_default_template_path(lang: str) -> str:
    return str(DEFAULT_TEMPLATE_DIR_PATH / "./default_template.{}".format(lang))
