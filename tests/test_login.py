import os
import unittest
from unittest import mock

from atcodertools.client.atcoder import LoginError
from atcodertools.tools import login


class FakeClient:
    def __init__(self, succeed=True):
        self.login_kwargs = None
        self.succeed = succeed
        self._session = mock.Mock()

    def login(self, **kwargs):
        self.login_kwargs = kwargs
        if not self.succeed:
            raise LoginError("invalid cookie")


class TestLogin(unittest.TestCase):

    def test_login_with_cookie_option_skips_cache_and_saves(self):
        client = FakeClient()
        with mock.patch(
                "atcodertools.tools.login.save_cookie") as mock_save:
            ok = login.main('', ['--cookie', 'abc'], client=client)
        self.assertTrue(ok)
        self.assertFalse(client.login_kwargs["use_local_session_cache"])
        self.assertFalse(client.login_kwargs["save_session_cache"])
        cookie = client.login_kwargs["cookie_supplier"]()
        self.assertEqual("REVEL_SESSION", cookie.name)
        self.assertEqual("abc", cookie.value)
        mock_save.assert_called_once_with(client._session)

    def test_login_with_env_var(self):
        client = FakeClient()
        with mock.patch.dict(
                "os.environ", {login.REVEL_SESSION_ENV_VAR: "xyz"}), \
                mock.patch("atcodertools.tools.login.save_cookie"):
            ok = login.main('', [], client=client)
        self.assertTrue(ok)
        cookie = client.login_kwargs["cookie_supplier"]()
        self.assertEqual("xyz", cookie.value)

    def test_login_interactive_when_no_cookie_given(self):
        client = FakeClient()
        env = {k: v for k, v in os.environ.items()
               if k != login.REVEL_SESSION_ENV_VAR}
        with mock.patch.dict("os.environ", env, clear=True):
            ok = login.main('', [], client=client)
        self.assertTrue(ok)
        self.assertIsNone(client.login_kwargs.get("cookie_supplier"))

    def test_login_failure_returns_false(self):
        client = FakeClient(succeed=False)
        ok = login.main('', ['--cookie', 'bad'], client=client)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
