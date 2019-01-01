import os


def _get_cache_dir_path():
    return os.path.join(os.path.expanduser('~/.local/share'), 'atcoder-tools')


def get_cache_file_path(filename: str):
    return os.path.join(_get_cache_dir_path(), filename)
