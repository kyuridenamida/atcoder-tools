class TokenManager:

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0

    def peek(self):
        assert not self.is_terminal()
        return self._tokens[self._pos]

    def is_terminal(self):
        return self._pos == len(self._tokens)

    def next(self):
        res = self.peek()
        self.go_next()
        return res

    def go_next(self):
        self._pos += 1

    def go_back(self):
        self._pos -= 1
