from typing import List


class TokenManager:

    def __init__(self, tokens: List[str]) -> None:
        self._tokens = tokens
        self._pos = 0

    def peek(self) -> str:
        assert not self.is_terminal()
        return self._tokens[self._pos]

    def is_terminal(self) -> bool:
        return self._pos == len(self._tokens)

    def next(self) -> str:
        res = self.peek()
        self.go_next()
        return res

    def go_next(self) -> None:
        self._pos += 1

    def go_back(self) -> None:
        self._pos -= 1
