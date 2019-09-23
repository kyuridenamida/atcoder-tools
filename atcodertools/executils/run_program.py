import subprocess
import time
from enum import Enum
from atcodertools.common.judgetype import JudgeType


class ExecStatus(Enum):
    NORMAL = "NORMAL"
    TLE = "TLE"
    RE = "RE"


def judge_decimal(out, ans: float, error_type: str, diff: float) -> bool:
    if error_type in ["absolute", "absolute_or_relative"] and abs(ans-out) <= diff:
        return True
    if error_type in ["relative", "absolute_or_relative"] and abs((ans-out)/ans) <= diff:
        return True
    return False


def judge_decimal_tokens(out, ans, error_type: str, diff: float) -> bool:
    out = out.strip().split()
    ans = ans.strip().split()
    if len(out) != len(ans):
        return False
    for i in range(0, len(out)):
        if not judge_decimal(float(out[i]), float(ans[i]), error_type, diff):
            return False
    return True


class ExecResult:

    def __init__(self, status: ExecStatus, output: str = None, stderr: str = None, elapsed_sec: float = None):
        self.status = status
        self.output = output
        self.stderr = stderr

        if elapsed_sec is not None:
            self.elapsed_ms = int(elapsed_sec * 1000 + 0.5)
        else:
            self.elapsed_ms = None

    def is_correct_output(self, answer_text, judge_type: JudgeType):
        if self.status != ExecStatus.NORMAL:
            return False
        if judge_type.judge_type == "normal":
            return answer_text == self.output
        elif judge_type.judge_type == "decimal":
            return judge_decimal_tokens(self.output, answer_text, judge_type.error_type, judge_type.diff)

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
        return ExecResult(ExecStatus.TLE, e.stdout, e.stderr)
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)
