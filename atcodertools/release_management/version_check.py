import json
import os
import time

import requests

from atcodertools.fileutils.artifacts_cache import get_cache_file_path


class VersionCheckError(Exception):
    pass


cache_file_path = get_cache_file_path('version_cache.txt')

HOUR_IN_SEC = 60 * 60


def _fetch_latest_version():
    dic = json.loads(requests.get(
        "https://pypi.org/pypi/atcoder-tools/json").text)
    return dic["info"]["version"]


def _get_latest_version_cache():
    if not os.path.exists(cache_file_path):
        return None
    with open(cache_file_path, 'r') as f:
        version, timestamp_sec = f.read().split()
        timestamp_sec = float(timestamp_sec)

        if time.time() - timestamp_sec > HOUR_IN_SEC:
            return None

        return version


def store_version_cache(version):
    os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
    with open(cache_file_path, 'w') as f:
        f.write("{} {}".format(version, time.time()))


def get_latest_version(use_cache=True):
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
