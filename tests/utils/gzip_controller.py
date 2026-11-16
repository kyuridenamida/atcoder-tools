import os
import shutil
import tarfile


class GZipController:
    def __init__(self, target_dir: str, gzip_file_path: str, main_dirname: str) -> None:
        self.target_dir = target_dir
        self.gzip_file_path = gzip_file_path
        self.main_dirname = main_dirname

    def create_dir(self) -> str:
        # `filter` kwarg exists on >=3.12 and on security backports
        # (3.9.17+/3.10.12+/3.11.4+); data_filter is added by the same patch.
        with tarfile.open(self.gzip_file_path, "r") as tf:
            if hasattr(tarfile, "data_filter"):
                tf.extractall(self.target_dir, filter="data")
            else:
                tf.extractall(self.target_dir)
        main_dir_path = os.path.join(self.target_dir, self.main_dirname)
        if os.path.exists(main_dir_path):
            return main_dir_path
        raise FileNotFoundError(f"{main_dir_path} is not found")

    def remove_dir(self) -> None:
        shutil.rmtree(self.target_dir)


def _make_data_full_path(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def make_tst_data_controller(target_dir: str) -> GZipController:
    return GZipController(target_dir, _make_data_full_path("../resources/common/test_data.tar.gz"), "test_data")


def make_html_data_controller(target_dir: str) -> GZipController:
    return GZipController(target_dir, _make_data_full_path("../resources/common/problem_htmls.tar.gz"), "problem_htmls")
