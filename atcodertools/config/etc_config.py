class EtcConfig:

    def __init__(self,
                 download_without_login: str = False,
                 parallel_download: bool = False,
                 save_no_session_cache: bool = False,
                 ):
        self.download_without_login = download_without_login
        self.parallel_download = parallel_download
        self.save_no_session_cache = save_no_session_cache
