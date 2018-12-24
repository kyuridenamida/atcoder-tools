#!/usr/bin/python3

import sys
import os
import glob
import subprocess
from pathlib import Path


def print_e(*text, end='\n'):
    print(*text, end=end, file=sys.stderr)


FAIL = ''
OKGREEN = ''
OKBLUE = ''
ENDC = ''


class NoExecutableFileError(Exception):
    pass


class IrregularInOutFileError(Exception):
    pass


class NoCppFileError(Exception):
    pass


class MultipleCppFilesError(Exception):
    pass


def is_executable_file(file_name):
    return os.access(file_name, os.X_OK) and Path(file_name).is_file() \
        and file_name.find(".cpp") == -1 and not file_name.endswith(".txt")  # cppやtxtを省くのは一応の Cygwin 対策


def do_test(exec_file=None):
    exec_files = [
        fname for fname in glob.glob(
            './*') if is_executable_file(
            fname)]
    if exec_file is None:
        if len(exec_files) == 0:
            raise NoExecutableFileError
        exec_file = exec_files[0]
        if len(exec_files) >= 2:
            print_e("WARNING: There're multiple executable files. This time, '%s' is selected." %
                    exec_file, "candidates =", exec_files)

    infiles = sorted(glob.glob('./in_*.txt'))
    outfiles = sorted(glob.glob('./out_*.txt'))

    success = 0
    total = 0

    for infile, outfile in zip(infiles, outfiles):
        if os.path.basename(infile)[2:] != os.path.basename(outfile)[3:]:
            print_e("The output for '%s' is not '%s'!!!" % (infile, outfile))
            raise IrregularInOutFileError
        with open(infile, "r") as inf, open(outfile, "r") as ouf:
            ans_data = ouf.read()
            out_data = ""
            status = "WA"
            try:
                out_data = subprocess.check_output(
                    [exec_file, ""], stdin=inf, universal_newlines=True, timeout=1)
            except subprocess.TimeoutExpired:
                status = "TLE(1s)"
            except subprocess.CalledProcessError:
                status = "RE"

            if out_data == ans_data:
                status = "PASSED"
                print_e("# %s ... %s" % (os.path.basename(infile),
                                         "%s%s%s" % (OKGREEN, status, ENDC)))
                success += 1
            else:
                print_e("# %s ... %s" % (os.path.basename(infile),
                                         "%s%s%s" % (FAIL, status, ENDC)))
                print_e("[Input]")
                with open(infile, "r") as inf2:
                    print_e(inf2.read(), end='')
                print_e("[Expected]")
                print_e("%s%s%s" %
                        (OKBLUE, ans_data, ENDC), end='')
                print_e("[Received]")
                print_e("%s%s%s" %
                        (FAIL, out_data, ENDC), end='')
                print_e()
        total += 1

    success_flag = False
    if total == 0:
        print_e("No test cases")
    elif success != total:
        print_e("Some cases FAILED (passed %s of %s)" % (success, total))
    else:
        print_e("Passed all testcases!!!")
        success_flag = True
    return success_flag


if __name__ == "__main__":
    if do_test():
        sys.exit(0)
    else:
        sys.exit(-1)
