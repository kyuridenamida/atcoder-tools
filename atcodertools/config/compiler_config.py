class CompilerConfig:

    def __init__(self,
                 compile_only_when_diff_detected: bool = False,
                 compile_command: str = None
                 ):
        self.compile_only_when_diff_detected = compile_only_when_diff_detected
        self.compile_command = compile_command
