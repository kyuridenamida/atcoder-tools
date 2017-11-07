import copy
from core.Calculator import CalcNode, CalcParseError

from core.utils import fixed_variable_name


def deviding_pattern(text, variables):
    """
            O(|text|^3)
            ある文字列を分割するパターンを考える．
            その際variablesに過去の変数の情報などをもたせ，インデックスとして今までに出てきたことのない変数が現れたら候補から除外するなどしている
            分割は3分割まで考える(2次元indexまで対応することを想定)
    """

    def is_variable_name(name):
        return all(c.isalpha() or c == '_' for c in name)

    def is_description(index):
        if not index[-1].isalpha() and not index[-1].isdigit():
            return False
        if index.find(',') != -1:
            return False
        return True

    candidate = [[text]]
    candidate += [[text[:i], text[i:]] for i in range(1, len(text))]
    for i in range(1, len(text)):
        for j in range(i + 1, len(text)):
            candidate += [[text[:i], text[i:j], text[j:]]]

    res = []
    for c in candidate:
        c = [x.rstrip(",") for x in c if x != ","]

        c[0] = fixed_variable_name(c[0])
        flag = True
        if not is_variable_name(c[0]):
            flag = False

        for index in c[1:]:
            if not is_description(index):
                flag = False
            try:
                for subvar in CalcNode(index).get_all_varnames():
                    if subvar not in variables:
                        flag = False
            except CalcParseError:
                flag = False
                pass

        if c[0] in variables and variables[c[0]] != len(c):
            flag = False

        if flag:
            res.append(c)
    return res


def dfs(final_answer, tokens, current_state, pos, variables, lim):
    """
            O(???) <-指数オーダー
            limの枝刈りのみで終了した場合はTrueが返ってくる
    """
    if len(variables) > lim:
        return True
    if pos == len(tokens):
        final_answer.append(copy.deepcopy(current_state))
        return False
    flag = False
    for d in deviding_pattern(tokens[pos], variables):
        next_vars = copy.deepcopy(variables)
        next_vars[d[0]] = len(d)
        current_state.append(d)
        if dfs(final_answer, tokens, current_state, pos + 1, next_vars, lim):
            flag = True
        current_state.pop()
    return flag


def get_all_format_probabilities(tokens):
    """
            入力
                    tokens#list(str) : 変数毎にパースされたトークン．これは不要な記号(…など)を含まない．　(例:["N","A_1","A_N"])
            出力
                    #list(list(list(str))) 出現する変数の数が最小となるような更なるtokenizeの組み合わせ全て．(例: [[["N"],["A_","1"],["A_","N"]]] )
            コメント
                    現実的なインスタンスは一瞬
    """
    final_answer = []
    lim = 1
    while len(final_answer) == 0:
        if not dfs(final_answer, tokens, [], 0, {}, lim):
            break
        lim += 1
    return final_answer
