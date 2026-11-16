#!/usr/bin/env python3
import sys
from typing import NoReturn

from colorama import Fore, Style

from atcodertools.release_management.version import __version__
from atcodertools.release_management.version_check import (
    VersionCheckError,
    get_latest_version,
)
from atcodertools.tools.codegen import main as codegen_main
from atcodertools.tools.compiler import main as compiler_main
from atcodertools.tools.envgen import main as envgen_main
from atcodertools.tools.setter import main as setter_main
from atcodertools.tools.submit import main as submit_main
from atcodertools.tools.tester import main as tester_main


def exit_program(success: bool) -> NoReturn:
    sys.exit(0 if success else -1)


def notify_if_latest_version_found() -> None:
    try:
        latest = get_latest_version()
        if latest != __version__:
            print(Fore.YELLOW, end="")
            print(f"The latest version {latest} is available! (The current version: {__version__})")
            print("To upgrade, run the following command:")
            print("")
            print("pip3 install atcoder-tools --upgrade")
            print(Style.RESET_ALL)
    except VersionCheckError:
        print(Fore.RED, end="")
        print("Failed to fetch the latest version information for some reason (maybe due to no internet connection?)")
        print(Style.RESET_ALL)


def main() -> None:
    notify_if_latest_version_found()

    if len(sys.argv) < 2 or sys.argv[1] not in ("gen", "test", "submit", "codegen", "set", "version", "compile"):
        print("Usage:")
        print(f"{sys.argv[0]} gen -- to generate workspace")
        print(f"{sys.argv[0]} test -- to test your code in the workspace")
        print(f"{sys.argv[0]} submit -- to submit your code to the contest system")
        print(f"{sys.argv[0]} compile -- compile source code")
        print(f"{sys.argv[0]} set -- switch program language/judge method")
        print(f"{sys.argv[0]} codegen -- to generate code of the specified single problem")
        print(f"{sys.argv[0]} version -- show atcoder-tools version")
        sys.exit(-1)

    prog = " ".join(sys.argv[:2])
    args = sys.argv[2:]

    if sys.argv[1] == "gen":
        envgen_main(prog, args)

    if sys.argv[1] == "test":
        exit_program(tester_main(prog, args))

    if sys.argv[1] == "submit":
        exit_program(submit_main(prog, args))

    if sys.argv[1] == "codegen":
        codegen_main(prog, args)

    if sys.argv[1] == "set":
        setter_main(prog, args)

    if sys.argv[1] == "compile":
        compiler_main(prog, args)

    if sys.argv[1] == "version":
        print(__version__)


if __name__ == "__main__":
    main()
