import os
import shutil
import tempfile
import unittest
from unittest import mock
from os.path import relpath
from logging import getLogger

from atcodertools.client.atcoder import AtCoderClient
from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.config.config import Config
from atcodertools.config.etc_config import EtcConfig
from atcodertools.tools.envgen import prepare_contest, main, EnvironmentInitializationError

logger = getLogger(__name__)

RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "./resources/test_atc_env/")
TEMPLATE_PATH = os.path.join(RESOURCE_DIR, "template.cpp")
REPLACEMENT_PATH = os.path.join(RESOURCE_DIR, "replacement.cpp")


def get_all_rel_file_paths(dir_path: str):
    res = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            res.append(relpath(os.path.join(root, filename), dir_path))
    return sorted(res)


class TestEnvGen(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        logger.info(self.temp_dir)

    def test_prepare_workspace(self):
        answer_data_dir_path = os.path.join(
            RESOURCE_DIR,
            "test_prepare_workspace")

        config_path = os.path.join(RESOURCE_DIR, "test_prepare_workspace.toml")

        main(
            "",
            ["agc029",
             "--workspace", self.temp_dir,
             "--template", TEMPLATE_PATH,
             "--lang", "cpp",
             "--without-login",
             '--config', config_path
             ]
        )
        self.assertDirectoriesEqual(answer_data_dir_path, self.temp_dir)

    def test_backup(self):
        answer_data_dir_path = os.path.join(RESOURCE_DIR, "test_backup")
        # Prepare workspace twice
        for _ in range(2):
            prepare_contest(
                AtCoderClient(),
                "agc029",
                Config(
                    code_style_config=CodeStyleConfig(
                        workspace_dir=self.temp_dir,
                        template_file=TEMPLATE_PATH,
                        lang="cpp",
                    ),
                    etc_config=EtcConfig(
                        in_example_format="input_{}.txt",
                        out_example_format="output_{}.txt"
                    ))
            )
        self.assertDirectoriesEqual(answer_data_dir_path, self.temp_dir)

    @mock.patch('time.sleep')
    def test_prepare_contest_aborts_after_max_retry_attempts(self, mock_sleep):
        mock_client = mock.Mock(spec=AtCoderClient)
        mock_client.download_problem_list.return_value = []
        self.assertRaises(
            EnvironmentInitializationError,
            prepare_contest,
            mock_client,
            "agc029",
            Config(
                code_style_config=CodeStyleConfig(
                    workspace_dir=self.temp_dir,
                    template_file=TEMPLATE_PATH,
                    lang="cpp",
                ),
                etc_config=EtcConfig(
                    in_example_format="input_{}.txt",
                    out_example_format="output_{}.txt"
                ))
        )
        self.assertEqual(mock_sleep.call_count, 10)
        mock_sleep.assert_has_calls([mock.call(1.5),
                                     mock.call(3.0),
                                     mock.call(6.0),
                                     mock.call(12.0),
                                     mock.call(24.0),
                                     mock.call(48.0),
                                     mock.call(60.0),
                                     mock.call(60.0),
                                     mock.call(60.0),
                                     mock.call(60.0)])

    def assertDirectoriesEqual(self, expected_dir_path, dir_path):
        files1 = get_all_rel_file_paths(expected_dir_path)
        files2 = get_all_rel_file_paths(dir_path)
        self.assertListEqual(files1, files2)

        for rel_file_path in files1:
            file_path1 = os.path.join(expected_dir_path, rel_file_path)
            file_path2 = os.path.join(dir_path, rel_file_path)

            with open(file_path1) as f1:
                with open(file_path2) as f2:
                    self.assertEqual(f1.read(), f2.read())


if __name__ == '__main__':
    unittest.main()
