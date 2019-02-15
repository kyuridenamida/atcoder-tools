#!/usr/bin/env python3

def solve(${formal_arguments}) -> None:
    return


def main():
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    ${input_part}
    solve(${actual_arguments})

if __name__ == '__main__':
    main()
