#!/usr/bin/python3
# -*- coding: utf-8 -*-

from AtCoder import AtCoder
import AccountInformation

		
atcoder = AtCoder(AccountInformation.username,AccountInformation.password)

plist = atcoder.get_problem_list("arc030")
print(atcoder.get_samples(plist['A']))