import os
import shutil
import tarfile

TEST_DATA_GZIP_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../resources/common/test_data.tar.gz')


class TestDataUtil:

    def __init__(self, target_dir):
        self.target_dir = target_dir

    def create_dir(self):
        tf = tarfile.open(TEST_DATA_GZIP_FILE, 'r')
        tf.extractall(self.target_dir)
        return os.path.join(self.target_dir, "test_data")

    def remove_dir(self):
        shutil.rmtree(self.target_dir)
