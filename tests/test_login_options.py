import argparse
import unittest

from atcodertools.config.etc_config import EtcConfig
from atcodertools.tools.utils import (
    ConflictingLoginOptionsError,
    decide_download_without_login,
)


def _args(with_login=None, without_login=None):
    return argparse.Namespace(
        with_login=with_login, without_login=without_login)


class TestDecideDownloadWithoutLogin(unittest.TestCase):

    def test_defaults_to_without_login(self):
        self.assertTrue(
            decide_download_without_login(_args(), EtcConfig()))

    def test_with_login_flag(self):
        self.assertFalse(
            decide_download_without_login(
                _args(with_login=True), EtcConfig()))

    def test_without_login_flag(self):
        self.assertTrue(
            decide_download_without_login(
                _args(without_login=True), EtcConfig()))

    def test_conflicting_flags(self):
        with self.assertRaises(ConflictingLoginOptionsError):
            decide_download_without_login(
                _args(with_login=True, without_login=True), EtcConfig())

    def test_config_download_with_login(self):
        self.assertFalse(
            decide_download_without_login(
                _args(), EtcConfig(download_with_login=True)))

    def test_config_download_without_login(self):
        self.assertTrue(
            decide_download_without_login(
                _args(), EtcConfig(download_without_login=True)))

    def test_conflicting_config(self):
        with self.assertRaises(ConflictingLoginOptionsError):
            decide_download_without_login(
                _args(),
                EtcConfig(
                    download_with_login=True,
                    download_without_login=True))

    def test_cli_overrides_config(self):
        self.assertFalse(
            decide_download_without_login(
                _args(with_login=True),
                EtcConfig(download_without_login=True)))
        self.assertTrue(
            decide_download_without_login(
                _args(without_login=True),
                EtcConfig(download_with_login=True)))


if __name__ == '__main__':
    unittest.main()
