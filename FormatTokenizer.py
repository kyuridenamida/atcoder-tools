import copy
from Calculator import calcNode
def deviding_pattern(text,vars):
	'''
		O(|text|^3)
		ある文字列を分割するパターンを考える．
		その際varsに過去の変数の情報などをもたせ，インデックスとして今までに出てきたことのない変数が現れたら候補から除外するなどしている
		分割は3分割まで考える(2次元indexまで対応することを想定)
	'''
	def is_variable_name(name):
		return all( c.isalpha() or c == '_' for c in name )

	def is_description(name):
		if not name[-1].isalpha() and not name[-1].isdigit():
			return False
		if name.find('_') != -1 :
			return False
		if name.find(',') != -1 :
			return False
		return True

	candidate = [[text]]
	candidate += [[text[:i],text[i:]] for i in range(1,len(text))]
	for i in range(1,len(text)):
		for j in range(i+1,len(text)):
			candidate += [[text[:i],text[i:j],text[j:]]]

	res = []
	for c in candidate:
		c = [x.rstrip(",") for x in c if x != ","]
		flag = True
		if not is_variable_name(c[0]): 
			flag = False
		for desc in c[1:]:
			if not is_description(desc):
				flag = False
			if is_variable_name(desc) and desc not in vars:
				flag = False
		
		if c[0] in vars and vars[c[0]] != len(c):
			flag = False;

		if flag:
			res.append(c)
	# print(res)
	return res


def dfs(finalAnswer,tokens,currentState,pos,vars,lim):
	'''
		O(???) <-指数オーダー
		limの枝刈りのみで終了した場合はTrueが返ってくる
	'''
	if len(vars) > lim :
		return True
	if pos == len(tokens):
		finalAnswer.append(copy.deepcopy(currentState))
		return False
	flag = False
	for d in deviding_pattern(tokens[pos],vars):
		nextVars = copy.deepcopy(vars)
		nextVars[d[0]] = len(d)
		currentState.append(d)
		if dfs(finalAnswer,tokens,currentState,pos+1,nextVars,lim) :
			flag = True
		currentState.pop()
	return flag

def get_all_format_probabilities(tokens):
	'''
		入力
			tokens#list(str) : 変数毎にパースされたトークン．これは不要な記号(…など)を含まない．　(例:["N","A_1","A_N"])
		出力
			#list(list(list(str))) 出現する変数の数が最小となるような更なるtokenizeの組み合わせ全て．(例: [[["N"],["A_","1"],["A_","N"]]] )
		コメント
			現実的なインスタンスは一瞬
	'''
	finalAnswer = []
	lim = 1
	while len(finalAnswer) == 0:
		if not dfs(finalAnswer,tokens,[],0,{},lim):
			break
		lim += 1
		# print(lim)
	return finalAnswer
