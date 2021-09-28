class SubmitConfig:

    def __init__(self,
                 exec_before_submit: str = None,
                 exec_after_submit: str = None,
                 submit_filename: str = None
                 ):
        self.exec_before_submit = exec_before_submit
        self.exec_after_submit = exec_after_submit
        self.submit_filename = submit_filename
