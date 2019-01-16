class EtcConfig:

    def __init__(self,
                 without_login: str = False,
                 parallel: bool = False,
                 save_no_session_cache: bool = False,
                 ):
        self.without_login = without_login
        self.parallel = parallel
        self.save_no_session_cache = save_no_session_cache