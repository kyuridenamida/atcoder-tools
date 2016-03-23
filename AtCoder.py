from utils import normalized

import urllib.request
from collections import OrderedDict
from bs4 import BeautifulSoup

import http.cookiejar
class LoginError(Exception): pass
class SampleParseError(Exception): pass

class AtCoder:
	def __init__(self,username,password):
		self.cj = http.cookiejar.CookieJar()
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		postdata = {
		    'name': username,
		    'password': password
		}
		encoded_postdata = urllib.parse.urlencode(postdata).encode('utf-8')
		req = self.opener.open("https://arc001.contest.atcoder.jp/login",encoded_postdata)
		html = req.read().decode('utf-8')
		if html.find("パスワードを忘れた方はこちら") != -1 :
			raise LoginError
	
	def get_problem_list(self,contestid):
		'''
			入力
				contestid#str : http://***.contest.atcoder.jp/)だったら***の部分
			出力
				#OrderedDict<str:str> : 問題番号("A","B","C",..)→URLのディクショナリ
		'''
		req = self.opener.open("http://%s.contest.atcoder.jp/assignments" % contestid)
		soup = BeautifulSoup(req,"html.parser")
		
		res = OrderedDict()

		for tag in soup.select('.linkwrapper')[0::2]:
			res[tag.text] = ("http://%s.contest.atcoder.jp" % contestid) + tag.get("href")
		return res

	def get_all(self,url):
		'''
			入力
				url#str : 問題ページのURL
			出力
				#(str,list((str,str))) : 指定したページから得られた(入力形式,[(サンプル入力1,出力1),(サンプル入力2,出力2)...]のリスト)の組
		'''
		req = self.opener.open(url)
		soup = BeautifulSoup(req,"html.parser")
		
		# AtCoder Formatぽかったらそっちはpartタグがついてていい感じなので，そっちを解析する
		soup_tmp = soup.select('.part')
		if soup_tmp != []:
			soup_tmp[0].extract()
		
		pretags = soup.select('pre')
		sample_tags = pretags[1:]
		input_tags = sample_tags[0::2]
		output_tags = sample_tags[1::2]
		if len(input_tags) != len(output_tags):
			raise SampleParseError
		res = [(normalized(in_tag.text),normalized(out_tag.text)) for in_tag,out_tag in zip(input_tags,output_tags)]
		input_format = normalized(pretags[0].text)
		return (input_format,res)

	def get_samples(self,url):
		'''
			入力
				url#str : 問題ページのURL
			出力
				 #list((str,str) : [(サンプル入力1,出力1),(サンプル入力2,出力2)...]のリスト
			コメント
				get_all()関数のwrapper
		'''
		return self.get_all(url)[1]