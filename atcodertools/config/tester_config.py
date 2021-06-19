class TesterConfig:

    def __init__(self,
                 compile_before_testing: bool = False,
                 compile_only_when_diff_detected: bool = False,
                 compile_command: str = None,
                 run_command: str = None
                 ):
        self.compile_before_testing = compile_before_testing
        self.compile_only_when_diff_detected = compile_only_when_diff_detected
        self.compile_command = compile_command
        self.run_command = run_command
