from os.path import expanduser
from typing import Optional, overload


@overload
def normalize_path(path: str) -> str: ...


@overload
def normalize_path(path: None) -> None: ...


def normalize_path(path: Optional[str]) -> Optional[str]:
    if path is None:
        return path
    return expanduser(path)
