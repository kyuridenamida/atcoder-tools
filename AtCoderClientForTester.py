#!/usr/bin/python3
import sys
import os
import glob
import subprocess
sys.path.append("core")
from AtCoder import AtCoder
import AccountInformation
from CppCodeGeneratorForTester import code_generator
import FormatPredictor
from multiprocessing import Pool
from multiprocessing import Process
from multiprocessing import cpu_count
from time import sleep
# このへんのコメントアウト弄るとカラフルじゃなくなったり，なったりします．
FAIL = '\033[91m'
OKGREEN = '\033[92m'
OKBLUE = '\033[94m'
ENDC = '\033[0m'
FAIL = OKGREEN = OKBLUE = ENDC = ''


class NoExecutableFileError(Exception):
    pass


class IrregularInOutFileError(Exception):
    pass


class NoCppFileError(Exception):
    pass


class MultipleCppFilesError(Exception):
    pass


def test_and_submit(contestid, pid, exec_file=None, cpp_file=None,
                    forced_submit_flag=False, no_submit_flag=False):
    
    exec_files = [fname for fname in glob.glob(
        './*') if os.access(fname, os.X_OK) and fname.find("test.py") == -1 and fname.find(".cpp") == -1 and not fname.endswith(".txt")] # cppやtxtを省くのは一応の Cygwin 対策
    if exec_file is None:
        if len(exec_files) == 0:
            raise NoExecutableFileError
        exec_file = exec_files[0]
        if len(exec_files) >= 2:
            print("WARNING: There're multiple executable files. This time, '%s' is selected." %
                  exec_file, "candidates =", exec_files)

    infiles = sorted(glob.glob('./in_*.txt'))
    outfiles = sorted(glob.glob('./out_*.txt'))

    succ = 0
    total = 0
    

    for infile, outfile in zip(infiles, outfiles):
        if os.path.basename(infile)[2:] != os.path.basename(outfile)[3:]:
            print("The output for '%s' is not '%s'!!!" % (infile, outfile))
            raise IrregularInOutFileError
        with open(infile, "r") as inf, open(outfile, "rb") as ouf:
            ans_data = ouf.read()
            out_data = ""
            status = "WA"
            try:
                out_data = subprocess.check_output(
                    [exec_file, ""], stdin=inf, timeout=1)
            except subprocess.TimeoutExpired:
                status = "TLE(1s)"
            except:
                status = "RE"

            if out_data == ans_data:
                status = "AC"
                print("# %s %s" % (os.path.basename(infile),
                                   "%s%s%s" % (OKGREEN, status, ENDC)))
                succ += 1
            else:
                print("# %s %s" % (os.path.basename(infile),
                                   "%s%s%s" % (FAIL, status, ENDC)))
                print("[Input]")
                with open(infile, "r") as inf2:
                    print(inf2.read(), end='')
                print("[Answer]")
                print("%s%s%s" % (OKBLUE, ans_data.decode('utf-8'), ENDC), end='')
                print("[Your output]")
                print("%s%s%s" % (FAIL, out_data.decode('utf-8'), ENDC), end='')
                print()
        total += 1

    if succ != total:
        print("Passed %d/%d testcases." % (succ, total))
    else:
        print("Passed all testcases!!!")

    if not no_submit_flag and ( total > 0 and succ == total or forced_submit_flag):
        atcoder = AtCoder(AccountInformation.username,
                          AccountInformation.password)

        if cpp_file is None:
            cpp_files = [fname for fname in glob.glob(
                './*') if fname.endswith(".cpp")]
            if len(cpp_files) != 1:
                if len(cpp_files) == 0:
                    raise NoCppFileError
                else:
                    raise MultipleCppFilesError
            cpp_file = cpp_files[0]

        print("Submitting...", end="")
        with open(cpp_file, "r") as f:
            if atcoder.submit_source_code(contestid, pid, "C\+\+1.*\(GCC", f.read()):
                print("%sdone%s" % (OKGREEN, ENDC))
                os.system(
                    "echo 'If you want to resubmit, delete this file.' > submission_lock_file")
            else:
                print("%sfailed%s" % (FAIL, ENDC))


pytemplate = \
    '''#!/usr/bin/python3
import sys
import os
sys.path.append("../../../")
sys.path.append("../../../core")
from AtCoderClient import test_and_submit

if __name__ == "__main__":
    forced_submit_flag = False
    if len(sys.argv) >= 2 and sys.argv[1] == "--f":
        forced_submit_flag = True
    no_submit_flag = False
    if os.path.exists("./submission_lock_file"):
        no_submit_flag = True
    test_and_submit(contestid='%s',pid='%s',no_submit_flag=no_submit_flag,forced_submit_flag=forced_submit_flag)
    if os.path.exists("./submission_lock_file"):
        print("Some solution has been submitted.")
'''



def prepare_procedure(argv):
    atcoder,pid,url = argv
    try:
        information, samples = atcoder.get_all(url)
        result = FormatPredictor.format_predictor(information, samples)
    except:
        result = None
        samples = []
        print("Problem %s: failed to get information." % pid)

    dirname = "workspace/%s/%s" % (contestid, pid)
    os.makedirs(dirname, exist_ok=True)

    # 既に存在しているならバックアップを取る
    solution_name = "%s/%s.cpp" % (dirname, pid)
    if os.path.exists(solution_name):
        backup_id = 1
        while True:
            backup_name = "%s.%d" % (solution_name, backup_id)
            if not os.path.exists(backup_name):
                os.system('cp "%s" "%s"' % (solution_name, backup_name))
                break
            backup_id += 1

    if result == None:
        print("Problem %s: failed to analyze input format." % pid)

    with open(solution_name, "w") as f:
        f.write(code_generator(result))

    with open("%s/test.py" % dirname, "w") as f:
        f.write(pytemplate % (contestid, pid))

    for num, (in_content, out_content) in enumerate(samples):
        casename = "%s_%d" % (pid, num + 1)
        infile = "%s/in_%s.txt" % (dirname, casename)
        outfile = "%s/out_%s.txt" % (dirname, casename)
        with open(infile, "w") as file:
            file.write(in_content)
        with open(outfile, "w") as file:
            file.write(out_content)
    os.system("notepad++ '%s/%s.cpp'" % (dirname,pid))
    print("prepared %s!" % pid)



def prepare_workspace(contestid):
    atcoder = AtCoder(AccountInformation.username, AccountInformation.password)

    while True:
        plist = atcoder.get_problem_list(contestid)
        if plist :
            break
        sleep(0.5)
        print("retrying to get task list.")
    #for pid,url in reversed([x for x in plist.items()]):

    while True:
        try:
            os.system('"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" %s' % plist['A'])
            break
        except:
            pass

    p = Pool(processes=cpu_count())

    p.map(prepare_procedure, [(atcoder,pid,url) for pid,url in plist.items()])

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        contestid = sys.argv[1]
        prepare_workspace(contestid)
    else:
        print("%s [contest_id]" % sys.argv[0])
