import json
import os
import time
from typing import Optional

import requests
from atcodertools.release_management.version import __version__
from atcodertools.fileutils.artifacts_cache import get_cache_file_path


class VersionCheckError(Exception):
    pass


cache_file_path = get_cache_file_path('version_cache.txt')

HOUR_IN_SEC = 60 * 60


def _fetch_latest_version() -> str:
    dic = json.loads(requests.get(
        "https://pypi.org/pypi/atcoder-tools/json").text)
    return str(dic["info"]["version"])


def _get_latest_version_cache() -> Optional[str]:
    if not os.path.exists(cache_file_path):
        return None
    with open(cache_file_path, 'r') as f:
        info = f.read().split()
        version, timestamp_sec_str = info[:2]

        if len(info) >= 3:
            captured_version = info[2]
        else:
            captured_version = None

        timestamp_sec = float(timestamp_sec_str)

        if time.time() - timestamp_sec > HOUR_IN_SEC or __version__ != captured_version:
            return None

        return version


def store_version_cache(version: str) -> None:
    os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
    with open(cache_file_path, 'w') as f:
        f.write("{} {} {}".format(version, time.time(), __version__))


def get_latest_version(use_cache: bool = True) -> str:
    try:
        if use_cache:
            cached_version = _get_latest_version_cache()
            if cached_version:
                return cached_version

        version = _fetch_latest_version()

        if use_cache:
            store_version_cache(version)

        return version
    except Exception:
        raise VersionCheckError
