import subprocess
import locale


def run_command(exec_cmd: str, current_working_dir: str) -> str:
    proc = subprocess.run(exec_cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          cwd=current_working_dir)
    return proc.stdout.decode(locale.getpreferredencoding())


def run_command_with_returncode(exec_cmd: str, current_working_dir: str):
    proc = subprocess.run(exec_cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          cwd=current_working_dir)
    return proc.returncode, proc.stdout.decode(locale.getpreferredencoding())
