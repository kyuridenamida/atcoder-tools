import os

DEFAULT_TEMPLATE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


def get_default_template_path(extension: str):
    return os.path.abspath(os.path.join(DEFAULT_TEMPLATE_DIR_PATH, "default_template.{}".format(extension)))
