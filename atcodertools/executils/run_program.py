import os
import subprocess
import sys
import time
from enum import Enum


class ExecStatus(Enum):
    NORMAL = "NORMAL"
    TLE = "TLE"
    RE = "RE"


# File extensions that are not executable on their own and need to be
# run through an interpreter (or a similar launcher). This fixes test
# runs on platforms where invoking a script directly fails, e.g.
# WinError 193 for .py files and "Exec format error" for .go files.
_INTERPRETER_COMMANDS = {
    ".py": [sys.executable],
    ".go": ["go", "run"],
    ".jl": ["julia"],
    ".rb": ["ruby"],
    ".pl": ["perl"],
}


def _resolve_exec_command(exec_file: str) -> list:
    """
    Build the argv list for the exec file.

    A path-like first token is resolved to an absolute path so that the
    executable can be found even when a working directory is given to
    subprocess.run (a relative path is otherwise looked up relative to
    that working directory).
    """
    tokens = exec_file.split(" ")
    first = tokens[0]

    has_sep = os.sep in first or (os.altsep is not None and os.altsep in first)
    if has_sep:
        first = os.path.abspath(first)
        tokens[0] = first

    ext = os.path.splitext(first)[1].lower()
    if ext in _INTERPRETER_COMMANDS and os.path.isfile(first):
        return _INTERPRETER_COMMANDS[ext] + tokens

    return tokens


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


def run_program(exec_file: str, input_file: str, timeout_sec: float, args=None, current_working_dir: str = None) -> ExecResult:
    if args is None:
        args = []
    try:
        elapsed_sec = -time.time()
        proc = subprocess.run(
            _resolve_exec_command(exec_file) + args, stdin=open(input_file, 'r'), universal_newlines=True, timeout=timeout_sec,
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
