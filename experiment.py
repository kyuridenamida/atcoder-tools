#!/usr/bin/python3
# -*- coding: utf-8 -*-

from AtCoder import AtCoder
import AccountInformation
import FormatAnalyzer
import FormatPredictor
import CppCodeGenerator

if __name__ == "__main__":
	
	atcoder = AtCoder(AccountInformation.username,AccountInformation.password)
	
	succ = fail = 0

	for i in range(1,50):
		plist = atcoder.get_problem_list("arc%03d"%i)
		
		for k,v in plist.items():
			try:
				informat,samples = atcoder.get_all(v)
				result = FormatPredictor.format_predictor(informat,samples)
				if result:
					print(CppCodeGenerator.code_generator(result))
				else:
					raise Exception

				# print("succ",v)
				succ += 1
			except KeyboardInterrupt:
				sys.exit(-1)
			except Exception as e:
				# print('=== エラー内容 ===')
				# print('type:' + str(type(e)))
				# print('e自身:' + str(e))
				print("fail,",v)
				pass
				fail += 1
			if(succ+fail>0):
				print (1.*succ/(succ+fail));