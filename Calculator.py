
class CalcParseError(Exception): pass
class EvaluteError(Exception): pass



class calcNode:
	def __init__(self,formula=None):
		if formula:
			root = parseToCalcNode(formula)
			self.content = root.content
			self.lch = root.lch
			self.rch = root.rch
			self.operator = root.operator
		else:
			self.content = None
			self.operator = None
			self.lch = None
			self.rch = None


	def get_all_varnames(self):
		if self.operator != None:
			lv = self.lch.get_all_varnames()
			rv = self.rch.get_all_varnames()
			return lv + rv
		elif isinstance(self.content,int):
				return []
		else:
			return [self.content]

	def evaluate(self,variables={}):
		if self.operator != None:
			lv = self.lch.evaluate(variables)
			rv = self.rch.evaluate(variables)
			return self.operator(lv,rv)
		elif isinstance(self.content,int):
				return int(self.content)
		else:
			if self.content not in variables:
				raise EvaluteError
			else:
				return variables[self.content]
		
def add(a,b):
	return a+b

def sub(a,b):
	return a-b

def mul(a,b):
	return a*b

def div(a,b):
	return int(a/b)

def expr(formula,pos):
	res,pos = term(formula,pos)
	while formula[pos] == '+' or formula[pos] == '-':
		tmp = calcNode()
		tmp.operator = add if formula[pos] == '+' else sub
		pos += 1
		tmp.lch = res
		tmp.rch,pos = term(formula,pos)
		res = tmp
	return res,pos
			

def term(formula,pos):
	res,pos = factor(formula,pos)
	while formula[pos] == '*' or formula[pos] == '/':
		tmp = calcNode()
		tmp.operator = mul if formula[pos] == '*' else div
		pos += 1
		tmp.lch = res
		tmp.rch,pos = factor(formula,pos)
		res = tmp
	return res,pos


def factor(formula,pos):
	if formula[pos] == '(':
		pos += 1
		res,pos = expr(formula,pos)
		if formula[pos] != ')':
			raise CalcParseError
		pos += 1
		return res,pos
	elif formula[pos].isalpha():
		varname = ""
		while formula[pos].isalpha():
			varname += formula[pos]
			pos += 1
		res = calcNode()
		res.content = varname
		return res,pos
	elif formula[pos].isdigit():
		value = 0
		while formula[pos].isdigit():
			value = 10 * value + int(formula[pos])
			pos += 1
		if formula[pos].isalpha() or formula[pos] == '(':
			# pattern like "123A"
			tmp = calcNode()
			tmp.content = value
			res = calcNode()
			res.lch = tmp
			res.rch,pos = factor(formula,pos)
			res.operator = mul
			return res,pos
		else:
			res = calcNode()
			res.content = value
			return res,pos
	else:
		raise CalcParseError



def parseToCalcNode(formula):
	'''
		入力
			formula # str : 式
		出力
			#calcNode : 構文木の根ノード

	'''
	res,pos = expr(formula+"$",0) #$は使わないことにする
	if pos != len(formula):
		raise CalcParseError
	return res

if __name__ == '__main__':

	print(calcNode("N-1-1+1000*N*N").evaluate({"N":10}))
