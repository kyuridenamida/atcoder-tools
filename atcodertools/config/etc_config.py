class EtcConfig:

    def __init__(self,
                 download_without_login: str = False,
                 parallel_download: bool = False,
                 save_no_session_cache: bool = False,
                 skip_existing_problems: bool = False,
                 in_example_format: str = "in_{}.txt",
                 out_example_format: str = "out_{}.txt",
                 compile_before_testing: bool = False,
                 compile_only_when_diff_detected: bool = False
                 ):
        self.download_without_login = download_without_login
        self.parallel_download = parallel_download
        self.save_no_session_cache = save_no_session_cache
        self.skip_existing_problems = skip_existing_problems
        self.in_example_format = in_example_format
        self.out_example_format = out_example_format
        self.compile_before_testing = compile_before_testing
        self.compile_only_when_diff_detected = compile_only_when_diff_detected
