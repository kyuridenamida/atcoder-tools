import subprocess
import time
from enum import Enum


class ExecStatus(Enum):
    NORMAL = "NORMAL"
    TLE = "TLE"
    RE = "RE"


class ExecResult:

    def __init__(self, status: ExecStatus, output: str = None, stderr: str = None, elapsed_sec: float = None):
        self.status = status
        self.output = output
        self.stderr = stderr

        if elapsed_sec is not None:
            self.elapsed_ms = int(elapsed_sec * 1000 + 0.5)
        else:
            self.elapsed_ms = None

    def is_correct_output(self, answer_text, judge_method):
        if self.status != ExecStatus.NORMAL:
            return False
        return judge_method.verify(self.output, answer_text)

    def has_stderr(self):
        return len(self.stderr) > 0


def run_program(exec_file: str, input_file: str, timeout_sec: int, args=None, current_working_dir: str = None) -> ExecResult:
    if args is None:
        args = []
    try:
        elapsed_sec = -time.time()
        proc = subprocess.run(
            [exec_file] + args, stdin=open(input_file, 'r'), universal_newlines=True, timeout=timeout_sec,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=current_working_dir
        )

        if proc.returncode == 0:
            code = ExecStatus.NORMAL
        else:
            code = ExecStatus.RE

        elapsed_sec += time.time()
        return ExecResult(code, proc.stdout, proc.stderr, elapsed_sec=elapsed_sec)
    except subprocess.TimeoutExpired as e:
        return ExecResult(ExecStatus.TLE, e.stdout or "", e.stderr or "")
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)
