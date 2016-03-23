#!/usr/bin/python3
# -*- coding: utf-8 -*-

from AtCoder import AtCoder

import AccountInformation

		
atcoder = AtCoder(AccountInformation.username,AccountInformation.password)

plist = atcoder.get_problem_list("arc049")

for pid,url in plist.items():
	samples = atcoder.get_samples(url)
	for num,(in_content,out_content) in zip(range(len(samples)),samples):
		casename = "./testcases/sample_%s_%d" % (pid,num+1)
		infile = "%s_in.txt" % casename
		outfile = "%s_out.txt" % casename
		with open(infile, "w") as file:
			file.write(in_content)
		with open(outfile, "w") as file:
			file.write(out_content)
