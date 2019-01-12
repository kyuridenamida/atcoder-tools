from os.path import expanduser
from typing import Optional


def normalize_path(path: Optional[str]) -> Optional[str]:
    if path is None:
        return path
    return expanduser(path)
