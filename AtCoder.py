import urllib.request
from collections import OrderedDict
from bs4 import BeautifulSoup
import http.cookiejar
class LoginError(Exception): pass
class SampleParseError(Exception): pass

class AtCoder:
	def __init__(self,username,password):
		self.cj = http.cookiejar.CookieJar() # クッキーを入れるコンテナみたいなの
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
		req = self.opener.open("http://%s.contest.atcoder.jp/assignments" % contestid)
		soup = BeautifulSoup(req,"html.parser")
		
		res = OrderedDict()

		for tag in soup.select('.linkwrapper')[0::2]:
			res[tag.text] = ("http://%s.contest.atcoder.jp" % contestid) + tag.get("href")
		return res

	def get_samples(self,url):
		req = self.opener.open(url)
		soup = BeautifulSoup(req,"html.parser")
		pretags = soup.select('pre')
		sample_tags = pretags[1:]
		input_tags = sample_tags[0::2]
		output_tags = sample_tags[1::2]
		if len(input_tags) != len(output_tags):
			raise SampleParseError
		res = [(in_tag.text.strip(),out_tag.text.strip()) for in_tag,out_tag in zip(input_tags,output_tags)]
		return res
