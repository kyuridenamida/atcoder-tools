import atexit
import functools
import os
import shutil
import tarfile
import tempfile


@functools.lru_cache(maxsize=None)
def _extract(gzip_file_path):
    # Extracting test_data.tar.gz takes tens of seconds, so do it once per test run rather than per test.
    # Tests only read the extracted files.
    extracted_dir = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, extracted_dir, ignore_errors=True)
    with tarfile.open(gzip_file_path, 'r') as tf:
        tf.extractall(extracted_dir)
    return extracted_dir


class GZipController:

    def __init__(self, target_dir, gzip_file_path, main_dirname):
        self.target_dir = target_dir
        self.gzip_file_path = gzip_file_path
        self.main_dirname = main_dirname

    def create_dir(self):
        main_dir_path = os.path.join(
            _extract(self.gzip_file_path), self.main_dirname)
        if os.path.exists(main_dir_path):
            return main_dir_path
        raise FileNotFoundError("{} is not found".format(main_dir_path))

    def remove_dir(self):
        shutil.rmtree(self.target_dir)


def _make_data_full_path(filename: str):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename)


def make_tst_data_controller(target_dir: str):
    return GZipController(target_dir,
                          _make_data_full_path(
                              '../resources/common/test_data.tar.gz'),
                          "test_data")


def make_html_data_controller(target_dir: str):
    return GZipController(target_dir,
                          _make_data_full_path(
                              '../resources/common/problem_htmls.tar.gz'),
                          "problem_htmls")
