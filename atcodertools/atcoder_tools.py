#!/usr/bin/env python3
import sys

from atcodertools.release_management.version_check import (
    get_latest_version,
    VersionCheckError,
)
from atcodertools.tools.envgen import main as envgen_main
from atcodertools.tools.tester import main as tester_main
from atcodertools.tools.submit import main as submit_main
from atcodertools.tools.codegen import main as codegen_main
from atcodertools.release_management.version import __version__
from colorama import Fore, Style


def exit_program(success: bool):
    sys.exit(0 if success else -1)


def notify_if_latest_version_found():
    try:
        latest = get_latest_version()
        if latest != __version__:
            print(Fore.YELLOW, end='')
            print("The latest version {0} is available! (The current version: {1})".format(
                latest, __version__))
            print("To upgrade, run the following command:")
            print("")
            print("pip3 install atcoder-tools --upgrade")
            print(Style.RESET_ALL)
    except VersionCheckError:
        print(Fore.RED, end='')
        print("Failed to fetch the latest version information "
              "for some reason (maybe due to no internet connection?)")
        print(Style.RESET_ALL)


def main():
    notify_if_latest_version_found()

    if len(sys.argv) < 2 or sys.argv[1] not in ("gen", "test", "submit", "codegen", "version"):
        print("Usage:")
        print("{} gen -- to generate workspace".format(sys.argv[0]))
        print("{} test -- to test codes in your workspace".format(sys.argv[0]))
        print(
            "{} submit -- to submit a code to the contest system".format(sys.argv[0]))
        print(
            "{} version -- show atcoder-tools version".format(sys.argv[0]))
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

    if sys.argv[1] == "version":
        print(__version__)
