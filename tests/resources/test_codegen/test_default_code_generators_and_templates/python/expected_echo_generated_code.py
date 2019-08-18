#!/usr/bin/env python3
import sys

MOD = 123  # type: int
YES = "yes"  # type: str
NO = "NO"  # type: str


def solve(N: int, M: int, H: "List[List[str]]", A: "List[int]", B: "List[float]", Q: int, X: "List[int]"):
    print(N, M)
    assert len(H) == N - 1
    for i in range(N - 1):
        assert len(H[i]) == M - 2
        print(*H[i])
    assert len(A) == N - 1
    assert len(B) == N - 1
    for i in range(N - 1):
        print(A[i], B[i])
    print(Q)
    assert len(X) == M + Q
    for i in range(M + Q):
        print(X[i])

    print(YES)
    print(NO)
    print(MOD)


def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    N = int(next(tokens))  # type: int
    M = int(next(tokens))  # type: int
    H = [[next(tokens) for _ in range(M - 1 - 2 + 1)] for _ in range(N - 2 + 1)]  # type: "List[List[str]]"
    A = [int()] * (N - 2 + 1)  # type: "List[int]"
    B = [float()] * (N - 2 + 1)  # type: "List[float]"
    for i in range(N - 2 + 1):
        A[i] = int(next(tokens))
        B[i] = float(next(tokens))
    Q = int(next(tokens))  # type: int
    X = [int(next(tokens)) for _ in range(M + Q)]  # type: "List[int]"
    solve(N, M, H, A, B, Q, X)

if __name__ == '__main__':
    main()
