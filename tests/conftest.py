"""pytest harness for atcoder-tools.

Design notes
------------
* ``tests/resources/**/*.py`` are programs-under-test executed as
  subprocesses by the tester, never pytest tests (see pyproject.toml's
  ``norecursedirs``).
* Tests that hit the real atcoder.jp are marked ``@pytest.mark.network``
  and skipped unless ``ATCODERTOOLS_TEST_NETWORK=1`` is set. They are
  flaky by nature (rate limiting, site changes) and must stay out of the
  default suite so that "tests pass == code is healthy" holds.
* Tests that compile/run generated code are marked ``requires_<lang>``
  and auto-skip when the toolchain is missing.
"""

import os
from collections.abc import Iterator

import pytest

from tests.utils.toolchains import (
    MARKER_TO_LANG,
    skip_reason_for,
    toolchain_available,
)


def _network_enabled() -> bool:
    return os.environ.get("ATCODERTOOLS_TEST_NETWORK") == "1"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    network_skip = pytest.mark.skip(reason="hits the real atcoder.jp; rerun with ATCODERTOOLS_TEST_NETWORK=1")
    for item in items:
        if "network" in item.keywords and not _network_enabled():
            item.add_marker(network_skip)
        for marker_name, lang_name in MARKER_TO_LANG.items():
            if marker_name in item.keywords and not toolchain_available(lang_name):
                item.add_marker(pytest.mark.skip(reason=skip_reason_for(lang_name)))


@pytest.fixture(autouse=True)
def _restore_cwd_after_test() -> Iterator[None]:
    """Tests such as test_config.py os.chdir() into resource dirs; without
    this the changed cwd would leak into subsequent tests and make results
    order-dependent."""
    cwd = os.getcwd()
    yield
    os.chdir(cwd)
