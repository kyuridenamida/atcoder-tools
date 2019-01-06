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
                 exec_on_each_problem_dir: str = None,
                 exec_on_contest_dir: str = None,
                 ):
        self.exec_cmd_on_problem_dir = exec_on_each_problem_dir
        self.exec_cmd_on_contest_dir = exec_on_contest_dir

    def execute_on_problem_dir(self, problem_dir: str) -> str:
        assert self.exec_cmd_on_problem_dir is not None
        return _run_command(self.exec_cmd_on_problem_dir, problem_dir)

    def execute_on_contest_dir(self, contest_dir: str) -> str:
        assert self.exec_cmd_on_contest_dir is not None
        return _run_command(self.exec_cmd_on_contest_dir, contest_dir)
