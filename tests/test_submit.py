import os
from typing import List, Sequence, Tuple
import unittest
from unittest import mock

import pytest

from atcodertools.client.models.submission import Submission
from atcodertools.tools import submit

RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_submit/"))


def fake_credential_suplier() -> Tuple[str, str]:
    return "@@fakeuser@@", "fakepass"


class TestTester(unittest.TestCase):

    def test_submit_fail_when_metadata_not_found(self) -> None:
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "without_metadata")], fake_credential_suplier, False)
        self.assertFalse(ok)

    @pytest.mark.network
    def test_test_fail(self) -> None:
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "with_metadata")], fake_credential_suplier, False)
        self.assertFalse(ok)


class TestSubmitWithMockClient(unittest.TestCase):
    """Offline equivalents of the submission flow: AtCoderClient is mocked,
    the local sample test runs for real (python3 only)."""

    def _run_submit(self, client: mock.Mock, extra_args: Sequence[str]=()) -> bool:
        with mock.patch("atcodertools.tools.submit.AtCoderClient",
                        return_value=client) as client_cls:
            return submit.main(
                '', ['-d', os.path.join(RESOURCE_DIR, "with_metadata")] + list(extra_args),
                fake_credential_suplier, False)

    def _make_client(self, submissions: List[Submission]) -> mock.Mock:
        client = mock.Mock()
        client.download_submission_list.return_value = submissions
        client.submit_source_code.return_value = Submission("arc001_1", 1)
        return client

    def test_submit_success_returns_true(self) -> None:
        # Regression: submit.main() used to return None on success, making
        # `atcoder-tools submit` exit non-zero even after a successful submit.
        client = self._make_client(submissions=[])
        self.assertTrue(self._run_submit(client))
        client.submit_source_code.assert_called_once()

    def test_submit_cancelled_by_safety_when_already_submitted(self) -> None:
        client = self._make_client(submissions=[Submission("arc001_1", 2)])
        self.assertFalse(self._run_submit(client))
        client.submit_source_code.assert_not_called()

    def test_submit_with_unlock_safety_resubmits(self) -> None:
        client = self._make_client(submissions=[Submission("arc001_1", 2)])
        self.assertTrue(self._run_submit(client, ["-u"]))
        client.submit_source_code.assert_called_once()

    def test_session_cache_is_saved_unless_disabled(self) -> None:
        # Regression: --save-no-session-cache used to be passed through
        # inverted (saving the cache when the user asked not to).
        client = self._make_client(submissions=[])
        self._run_submit(client)
        self.assertTrue(client.login.call_args[1]["save_session_cache"])

        client = self._make_client(submissions=[])
        self._run_submit(client, ["--save-no-session-cache"])
        self.assertFalse(client.login.call_args[1]["save_session_cache"])

    def test_submit_fails_when_local_test_fails(self) -> None:
        client = self._make_client(submissions=[])
        ok = submit.main(
            '', ['-d', os.path.join(RESOURCE_DIR, "without_metadata")],
            fake_credential_suplier, False)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
