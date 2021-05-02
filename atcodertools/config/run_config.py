from typing import Optional


class RunConfig:

    def __init__(self,
                 compile_command: Optional[str] = None,
                 run_command: Optional[str] = None
                 ):
        self.compile_command = compile_command
        self.run_command = run_command
