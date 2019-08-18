#!/usr/bin/env python3
{% if prediction_success %}
import sys
{% endif %}
{% if mod or yes_str or no_str %}

{% endif %}
{% if mod %}
MOD = {{ mod }}  # type: int
{% endif %}
{% if yes_str %}
YES = "{{ yes_str }}"  # type: str
{% endif %}
{% if no_str %}
NO = "{{ no_str }}"  # type: str
{% endif %}
{% if prediction_success %}


def solve({{ formal_arguments }}):
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
{% endif %}


def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    {{ input_part }}
    solve({{ actual_arguments }})

if __name__ == '__main__':
    main()
