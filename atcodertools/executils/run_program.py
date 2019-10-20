import subprocess
import time
from enum import Enum
import threading
from atcodertools.common.judgetype import JudgeType
import tempfile


class ExecStatus(Enum):
    NORMAL = "NORMAL"
    TLE = "TLE"
    RE = "RE"


class JudgeStatus(Enum):
    AC = "AC"
    WA = "WA"


class ExecResult:
    def __init__(self, status: ExecStatus, output: str = None, stderr: str = None, elapsed_sec: float = None, special_judge_status: JudgeStatus = None, judge_message: str = None):
        self.status = status
        self.output = output
        self.stderr = stderr
        self.special_judge_status = special_judge_status
        self.judge_message = judge_message

        if elapsed_sec is not None:
            self.elapsed_ms = int(elapsed_sec * 1000 + 0.5)
        else:
            self.elapsed_ms = None

    def is_correct_output(self, expected_answer_text=None, judge_method=None, sample_input_file=None, sample_output_file=None):
        if self.status != ExecStatus.NORMAL:
            return False
        if self.special_judge_status is not None:
            return self.special_judge_status == JudgeStatus.AC

        if judge_method.judge_type == JudgeType.MultiSolution:
            judge_exec_res = run_multisolution_judge_program(judge_method.judge_exec_file,
                                                             self.output,
                                                             sample_input_file,
                                                             sample_output_file
                                                             )
            self.judge_message = judge_exec_res.stderr
            return judge_exec_res.special_judge_status == JudgeStatus.AC
        elif judge_method.judge_type == JudgeType.Interactive:
            raise("No judge status error for interactive!!")
        else:
            return judge_method.verify(self.output, expected_answer_text)

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


def run_multisolution_judge_program(exec_judge_file: str, output: str, sample_input_file: str, sample_output_file: str, args=None, current_working_dir: str = None) -> ExecResult:
    if args is None:
        args = []
    try:
        tf = tempfile.TemporaryFile()
        tf.write(output.encode())
        tf.seek(0)
        proc = subprocess.run(
            [exec_judge_file, sample_input_file, sample_output_file] + args,
            stdin=tf, universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=current_working_dir
        )

        code = ExecStatus.NORMAL

        if proc.returncode == 0:
            judge_status = JudgeStatus.AC
        elif proc.returncode == 1:
            judge_status = JudgeStatus.WA
        else:
            judge_status = JudgeStatus.WA
            code = ExecStatus.RE

        return ExecResult(code, proc.stdout, proc.stderr, special_judge_status=judge_status, judge_message=proc.stderr)
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)


def run_interactive_program(exec_file: str, exec_judge_file: str, input_file: str,
                            output_file: str, timeout_sec: int, args=None,
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
        else:
            print("Your judge program may be incorrect")
            print(main_thread.status)
            print(judge_thread.status)

        elapsed_sec += time.time()
        return ExecResult(code, judge_thread.proc.stderr.read().decode(), main_thread.proc.stderr.read().decode(),
                          elapsed_sec=elapsed_sec, special_judge_status=judge_status)
    except subprocess.TimeoutExpired as e:
        return ExecResult(ExecStatus.TLE, e.stdout, e.stderr)
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)
