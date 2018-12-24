import glob
import os
import shutil
import tempfile
import unittest
from os.path import relpath
from unittest.mock import patch

from client.AtCoderClient import AtCoderClient
from tools.atc_env import prepare_workspace
from tools.tester import is_executable_file

RESOURCE_DIR = "./resources/TestAtCoderEnv/"
TEMPLATE_PATH = os.path.join(RESOURCE_DIR, "template.cpp")
REPLACEMENT_PATH = os.path.join(RESOURCE_DIR, "replacement.cpp")


def get_all_rel_file_paths(dir_path: str):
    res = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            res.append(relpath(os.path.join(root, filename), dir_path))
    return res


class TestAtCoderEnv(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_prepare_workspace(self):
        answer_data_dir_path = os.path.join(RESOURCE_DIR, "test_prepare_workspace")
        prepare_workspace(AtCoderClient(), "agc029", self.temp_dir, TEMPLATE_PATH, REPLACEMENT_PATH, False)
        self.assertDirectoriesEqual(answer_data_dir_path, self.temp_dir)

    def test_backup(self):
        answer_data_dir_path = os.path.join(RESOURCE_DIR, "test_backup")
        # Prepare workspace twice
        for _ in range(2):
            prepare_workspace(AtCoderClient(), "agc029", self.temp_dir, TEMPLATE_PATH, REPLACEMENT_PATH, False)
        print(self.temp_dir)
        self.assertDirectoriesEqual(answer_data_dir_path, self.temp_dir)

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