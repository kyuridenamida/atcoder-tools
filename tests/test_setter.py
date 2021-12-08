import os
import shutil
import tempfile
import unittest
from os.path import relpath
from logging import getLogger

from atcodertools.tools.setter import main
from atcodertools.tools.models.metadata import Metadata
from atcodertools.common.language import JAVA
from atcodertools.common.judgetype import ErrorType

logger = getLogger(__name__)

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_setter/")
TEMPLATE_PATH = os.path.join(RESOURCE_DIR, "template.cpp")
REPLACEMENT_PATH = os.path.join(RESOURCE_DIR, "replacement.cpp")


def get_all_rel_file_paths(dir_path: str):
    res = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            res.append(relpath(os.path.join(root, filename), dir_path))
    return sorted(res)


class TestSetter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        logger.info(self.temp_dir)

    def test_setter_change_lang(self):
        test_dir = os.path.join(self.temp_dir, "test_setter")
        shutil.copytree(os.path.join(RESOURCE_DIR, "test"), test_dir)
        # abc117A

        main(
            "",
            ["--lang", "java",
             "--dir", test_dir,
             "--without-login"]
        )
        self.assertEqual(open(os.path.join(test_dir, "main.java")).read(),
                         open(os.path.join(RESOURCE_DIR, "ans", "main.java")).read())

        metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
        self.assertEqual(metadata.lang, JAVA)

        main(
            "",
            ["--judge-type", "relative",
             "--dir", test_dir]
        )

        metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
        self.assertEqual(metadata.judge_method.error_type, ErrorType.Relative)

        main(
            "",
            ["--error-value", "1e-7",
             "--dir", test_dir]
        )
        metadata = Metadata.load_from(os.path.join(test_dir, "metadata.json"))
        self.assertTrue(abs(metadata.judge_method.diff - 1e-7)
                        < 1e-11)  # TODO: これでいいのか？


if __name__ == '__main__':
    unittest.main()
