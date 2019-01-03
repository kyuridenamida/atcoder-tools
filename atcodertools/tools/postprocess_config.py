import subprocess


def _run_command(exec_cmd: str, current_working_dir: str) -> str:
    proc = subprocess.run(exec_cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          cwd=current_working_dir)
    return proc.stdout.decode("utf8")


class PostprocessConfig:
    def __init__(self,
                 exec_after_problem_created: str = None,
                 exec_after_contest_created: str = None,
                 ):
        self.exec_after_problem_created = exec_after_problem_created
        self.exec_after_contest_created = exec_after_contest_created

    def run_exec_after_problem_created(self, problem_dir: str) -> str:
        assert self.exec_after_problem_created is not None
        return _run_command(self.exec_after_problem_created, problem_dir)

    def run_exec_after_contest_created(self, workspace_dir: str) -> str:
        assert self.exec_after_contest_created is not None
        return _run_command(self.exec_after_contest_created, workspace_dir)
