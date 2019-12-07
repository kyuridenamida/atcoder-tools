from enum import Enum


class CompileType(Enum):
    OFF = "off"
    ON = "on"
    FORCE = "force"


class EtcConfig:

    def __init__(self,
                 download_without_login: str = False,
                 parallel_download: bool = False,
                 save_no_session_cache: bool = False,
                 in_example_format: str = "in_{}.txt",
                 out_example_format: str = "out_{}.txt",
                 compile_type: CompileType = CompileType.OFF
                 ):
        self.download_without_login = download_without_login
        self.parallel_download = parallel_download
        self.save_no_session_cache = save_no_session_cache
        self.in_example_format = in_example_format
        self.out_example_format = out_example_format
        self.compile_type = CompileType(compile_type)
