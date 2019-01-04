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
                 exec_cmd_for_problem: str = None,
                 exec_cmd_for_contest: str = None,
                 ):
        self.exec_cmd_for_problem = exec_cmd_for_problem
        self.exec_cmd_for_contest = exec_cmd_for_contest

    def execute_for_problem(self, problem_dir: str) -> str:
        assert self.exec_cmd_for_problem is not None
        return _run_command(self.exec_cmd_for_problem, problem_dir)

    def execute_for_contest(self, workspace_dir: str) -> str:
        assert self.exec_cmd_for_contest is not None
        return _run_command(self.exec_cmd_for_contest, workspace_dir)
