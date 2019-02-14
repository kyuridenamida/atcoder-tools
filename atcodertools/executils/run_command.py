import subprocess


def run_command(exec_cmd: str, current_working_dir: str) -> str:
    proc = subprocess.run(exec_cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          cwd=current_working_dir)
    return proc.stdout.decode("utf8")
