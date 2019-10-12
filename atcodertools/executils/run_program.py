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


AC_TAG = "<<<AC>>>"
WA_TAG = "<<<WA>>>"


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


log = ""
lock_log = threading.Lock()


def run_interactive_program(exec_file: str, exec_judge_file: str, input_file: str,
                            output_file, timeout_sec: int, args=None,
                            current_working_dir: str = None) -> ExecResult:
    global log
    if args is None:
        args = []
    try:
        elapsed_sec = -time.time()

        main_proc = subprocess.Popen([exec_file],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=current_working_dir
                                     )
        judge_proc = subprocess.Popen([exec_judge_file, input_file, output_file],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      cwd=current_working_dir
                                      )

        log = "Input         Output\n"
        log += "----------------------\n"

        with open(input_file, "r") as f:
            for line in f:
                main_proc.stdin.write(line.encode())
        main_proc.stdin.flush()

        class PollMain(threading.Thread):
            def __init__(self, main_proc, judge_proc):
                threading.Thread.__init__(self)
                self.main_proc = main_proc
                self.judge_proc = judge_proc
                pass

            def run(self):
                global log, lock_log
                while True:
                    if self.main_proc.poll() is not None:
                        break
                    out = self.main_proc.stdout.readline().decode()
                    if out == '':
                        continue
                    lock_log.acquire()
                    log += out
                    lock_log.release()
                    judge_proc.stdin.write(out.encode())
                    judge_proc.stdin.flush()

        class PollJudge(threading.Thread):
            def __init__(self, main_proc, judge_proc):
                threading.Thread.__init__(self)
                self.main_proc = main_proc
                self.judge_proc = judge_proc
                pass

            def run(self):
                global log, lock_log
                while True:
                    if self.judge_proc.poll() is not None or self.main_proc.poll() is not None:
                        break
                    out = judge_proc.stdout.readline().decode()
                    lock_log.acquire()
                    log += "              " + out
                    lock_log.release()
                    main_proc.stdin.write(out.encode())
                    main_proc.stdin.flush()

        main_thread = PollMain(main_proc, judge_proc)
        judge_thread = PollJudge(main_proc, judge_proc)

        main_thread.start()
        judge_thread.start()

        main_proc.wait()
        judge_proc.wait()

        judge_status = None
        if judge_proc.returncode == 0:
            judge_status = JudgeStatus.AC
        elif judge_proc.returncode == 1:
            judge_status = JudgeStatus.WA
        else:
            print("ERROR!!!!")
            assert(False)

        if main_proc.returncode == 0:
            code = ExecStatus.NORMAL
        else:
            code = ExecStatus.RE

        elapsed_sec += time.time()
        err = ""
        for line in main_proc.stderr:
            err += line.decode()
        return ExecResult(code, log, err, elapsed_sec=elapsed_sec, judge_status=judge_status)
    except subprocess.TimeoutExpired as e:
        return ExecResult(ExecStatus.TLE, e.stdout, e.stderr)
    except subprocess.CalledProcessError as e:
        return ExecResult(ExecStatus.RE, e.stdout, e.stderr)
