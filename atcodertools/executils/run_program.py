import subprocess
import time
from enum import Enum
import threading


class ExecStatus(Enum):
    NORMAL = "NORMAL"
    TLE = "TLE"
    RE = "RE"


class JudgeStatus(Enum):
    AC = "AC"
    WA = "WA"


class ExecResult:

    def __init__(self, status: ExecStatus, output: str = None, stderr: str = None, elapsed_sec: float = None, judge_status: JudgeStatus = None):
        self.status = status
        self.output = output
        self.stderr = stderr
        self.judge_status = judge_status

        if elapsed_sec is not None:
            self.elapsed_ms = int(elapsed_sec * 1000 + 0.5)
        else:
            self.elapsed_ms = None

    def is_correct_output(self, answer_text=None, judge_method=None):
        if self.status != ExecStatus.NORMAL:
            return False
        if self.judge_status is None:
            if judge_method.verify(self.output, answer_text):
                self.judge_status = JudgeStatus.AC
            else:
                self.judge_status = JudgeStatus.WA
        return self.judge_status == JudgeStatus.AC

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


def run_interactive_program(exec_file: str, exec_judge_file: str, input_file: str,
                            output_file, timeout_sec: int, args=None,
                            current_working_dir: str = None) -> ExecResult:
    if args is None:
        args = []
    try:
        elapsed_sec = -time.time()

        class RunThread(threading.Thread):
            def __init__(self, cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input_file=None, timeout_sec=None):
                threading.Thread.__init__(self)
                self.proc = subprocess.Popen(cmd + args,
                                             stdin=stdin,
                                             stdout=stdout,
                                             stderr=stderr,
                                             cwd=current_working_dir
                                             )
                self.timeout_sec = timeout_sec
                self.input_file = input_file

            def __exit__(self, type, value, traceback):
                self.close()

            def run(self):
                try:
                    if self.timeout_sec is not None:
                        self.return_code = self.proc.wait(
                            timeout=self.timeout_sec)
                    else:
                        self.return_code = self.proc.wait()
                    self.status = ExecStatus.NORMAL
                except (SystemError, OSError):
                    self.status = ExecStatus.RE
                except subprocess.TimeoutExpired:
                    self.status = ExecStatus.TLE

            def close(self):
                self.proc.stdin.close()

        main_thread = RunThread(
            [exec_file], input_file=input_file, timeout_sec=timeout_sec)
        judge_thread = RunThread([exec_judge_file, input_file, output_file],
                                 stdin=main_thread.proc.stdout,
                                 stdout=main_thread.proc.stdin,
                                 timeout_sec=timeout_sec + 1)

        main_thread.start()
        judge_thread.start()

        main_thread.join()
        judge_thread.join()

        judge_status = None
        if judge_thread.status == ExecStatus.NORMAL:
            if main_thread.status != ExecStatus.NORMAL:
                print("main thread didn't ended normally after judge")
                code = main_thread.status
            else:
                code = ExecStatus.NORMAL
                if judge_thread.return_code == 0:
                    judge_status = JudgeStatus.AC
                else:
                    judge_status = JudgeStatus.WA
        elif main_thread.status == ExecStatus.RE:
            code = ExecStatus.RE
        elif main_thread.status == ExecStatus.TLE:
            code = ExecStatus.TLE

        elapsed_sec += time.time()
        err = ""
#        for line in main_thread.proc.stderr:
#            err += line.decode()
        log = open("./log").read()
        return ExecResult(code, log, err, elapsed_sec=elapsed_sec, judge_status=judge_status)
    except subprocess.TimeoutExpired as e:
        return ExecResult(ExecStatus.TLE, e.stdout, e.stderr)
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)
