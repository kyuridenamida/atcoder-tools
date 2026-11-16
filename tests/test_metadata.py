import unittest

from atcodertools.common.judgetype import NormalJudge
from atcodertools.tools.models.metadata import Metadata


class TestMetadata(unittest.TestCase):
    def test_default_judge_method_is_not_shared_between_instances(self) -> None:
        # Regression: the default argument used to be a single shared
        # NormalJudge() instance, so mutating one Metadata's judge_method
        # (e.g. `atcoder-tools set -j decimal -v 1e-5` tweaking diff) would
        # leak into every other Metadata built afterwards.
        first = Metadata(None, None, "in_*.txt", "out_*.txt", None)
        second = Metadata(None, None, "in_*.txt", "out_*.txt", None)
        self.assertIsNot(first.judge_method, second.judge_method)
        first.judge_method.diff = 0.1  # type: ignore[attr-defined]
        self.assertFalse(hasattr(second.judge_method, "diff"))

    def test_explicit_judge_method_is_used(self) -> None:
        judge = NormalJudge()
        metadata = Metadata(None, None, "in_*.txt", "out_*.txt", None, judge_method=judge)
        self.assertIs(judge, metadata.judge_method)


if __name__ == "__main__":
    unittest.main()
