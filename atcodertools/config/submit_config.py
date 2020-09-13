from typing import Optional


class SubmitConfig:

    def __init__(self,
                 run_exec_before_submit: bool = False,
                 exec_before_submit: Optional[str] = None,
                 submit_filename: Optional[str] = None
                 ):
        self.run_exec_before_submit = run_exec_before_submit
        self.exec_before_submit = exec_before_submit
        self.submit_filename = submit_filename
