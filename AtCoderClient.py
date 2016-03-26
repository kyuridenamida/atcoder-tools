import os
import glob
import subprocess
from AtCoder import AtCoder 
import AccountInformation 
from CppCodeGenerator import code_generator

FAIL = '\033[91m'
OKGREEN = '\033[92m'
OKBLUE = '\033[94m'
ENDC = '\033[0m'

class NoExecutableFileError(Exception): pass
class IrregularInOutFileError(Exception): pass
class NoCppFileError(Exception): pass
class MultipleCppFilesError(Exception): pass

def test_and_submit(contestid,pid,exec_file=None,cpp_file=None,
					forced_submit_flag=False,no_submit_flag=False):
	exec_files = [fname for fname in glob.glob('./*') if os.access(fname,os.X_OK) and fname != "./test.py" ]

	if exec_file is None:
		if len(exec_files) == 0:
			raise NoExecutableFileError
		exec_file = exec_files[0]	
		if len(exec_files) >= 2:
			print("WARNING: There're multiple executable files. This time, '%s' is selected." % exec_file,"candidates =",exec_files)

	infiles = sorted(glob.glob('./in_*.txt'))
	outfiles = sorted(glob.glob('./out_*.txt'))

	succ = 0
	total = 0
	for infile,outfile in zip(infiles,outfiles):
		if os.path.basename(infile)[2:] != os.path.basename(outfile)[3:]:
			print("The output for '%s' is not '%s'!!!" % (infile,outfile) )
			raise IrregularInOutFileError
		with open(infile, "r") as inf, open(outfile, "rb") as ouf:
			ans_data = ouf.read()
			out_data = subprocess.check_output([exec_file, ""],stdin=inf)
			if out_data == ans_data:
				print("# %s %s" % (os.path.basename(infile),"%sPassed%s"%(OKGREEN,ENDC)))
				succ += 1
			else:
				print("# %s %s" % (os.path.basename(infile),"%sFailed%s"%(FAIL,ENDC)))
				print("[Input]")
				with open(infile, "r") as inf2:
					print(inf2.read(),end='')
				print("[Answer]")
				print("%s%s%s"%(OKBLUE,ans_data.decode('utf-8'),ENDC), end='')
				print("[Your output]")
				print("%s%s%s"%(FAIL,out_data.decode('utf-8'),ENDC), end='')
				print()
		total += 1

	if succ != total:
		print("Passed %d/%d testcases."%(succ,total))
	else:
		print("Passed all testcases!!!")
	
	if not no_submit_flag and (succ == total or forced_submit_flag) :
		atcoder = AtCoder(AccountInformation.username,AccountInformation.password)

		if cpp_file is None:
			cpp_files = [fname for fname in glob.glob('./*') if fname.endswith(".cpp") ]
			if len(cpp_files) != 1:
				if len(cpp_files) == 0:
					raise NoCppFileError
				else:
					raise MultipleCppFilesError
			cpp_file = cpp_files[0]

		print("Submitting...",end="")
		with open(cpp_file, "r") as f:
			if atcoder.submit_source_code(contestid,pid,"C\+\+1.*\(GCC",f.read()):
				print("%sdone%s"%(OKGREEN,ENDC))
			else:
				print("%sfailed%s"%(FAIL,ENDC))

def prepare_workspace(contestid):
	atcoder = AtCoder(AccountInformation.username,AccountInformation.password)
	plist = atcoder.get_problem_list(contestid)
	for pid,url in plist.items():
		information,samples = atcoder.get_all(url)
		result = FormatPredictor.format_predictor(information,samples)

		dirname = "workspace/%s/%s" % (contestid,pid)
		os.makedirs(dirname, exist_ok=True)

		with open("%s/%s.cpp" % (dirname,pid), "w") as f:
			f.write(code_generator(result))

		try:
			samples = atcoder.get_samples(url)
		except:
			print("Problem %s: failed to get samples...." % pid)

		for num,(in_content,out_content) in enumerate(samples):
			casename = "%s_%d" % (pid,num+1)
			infile = "%s/in_%s.txt" % (dirname,casename)
			outfile = "%s/out_%s.txt" % (dirname,casename)
			with open(infile, "w") as file:
				file.write(in_content)
			with open(outfile, "w") as file:
				file.write(out_content)



if __name__ == "__main__":
	import sys
	from functools import reduce
	import AccountInformation
	from AtCoder import AtCoder
	import FormatPredictor	
	import os

	if len(sys.argv) == 3:
		contestid = sys.argv[1]
		pid = sys.argv[2]
		atcoder = AtCoder(AccountInformation.username,AccountInformation.password)
		
		plist = atcoder.get_problem_list(contestid)
		url = plist[pid]
		information,samples = atcoder.get_all(url)
		
		result = FormatPredictor.format_predictor(information,samples)
		dirname = "workspace/%s" % pid
		os.makedirs(dirname, exist_ok=True)
		
		if not result:
			raise Exception
		with open("%s/%s.cpp" % (dirname,pid), "w") as f:
			f.write(code_generator(result))

		samples = atcoder.get_samples(url)
		for num,(in_content,out_content) in enumerate(samples):
			casename = "%s_%d" % (pid,num+1)
			infile = "%s/in_%s.txt" % (dirname,casename)
			outfile = "%s/out_%s.txt" % (dirname,casename)
			with open(infile, "w") as file:
				file.write(in_content)
			with open(outfile, "w") as file:
				file.write(out_content)
		#with open("%s/%s.cpp" % (dirname,pid), "w") as f:
		#	atcoder.submit_source_code(contestid,pid,"C\+\+1.*\(GCC",f.read())

	else:
		print("# of argvs must be 2 (contestid(ex:arc001) and problemid(ex:A)).")
