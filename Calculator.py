
class CalcParseError(Exception): pass
class EvaluteError(Exception): pass



class calcNode:
	def __init__(self):
		self.content = None
		self.operator = None
		self.lch = None
		self.rch = None

	def evalute(self,vars={}):
		if self.operator != None:
			lv = self.lch.evalute(vars)
			rv = self.rch.evalute(vars)
			return self.operator(lv,rv)
		else:
			if isinstance(self.content,int):
				return int(self.content)
			else:
				if self.content not in vars:
					raise EvaluteError
				else:
					return vars[self.content]
		
def add(a,b):
	return a+b
def sub(a,b):
	return a-b
def mul(a,b):
	return a*b
def div(a,b):
	return int(a/b)

formula = ""
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
		res = calcNode()
		res.content = value
		return res,pos
	else:
		raise CalcParseError


def parseToNode(formula):
	res,pos = expr(formula+"$",0) #$は使わないことにする
	if pos != len(formula):
		raise CalcParseError
	return res

if __name__ == '__main__':

	print(parseToNode("N-1-1+1000*N*N").evalute({"N":10}))
