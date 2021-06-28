package main

import (
	"bufio"
	"os"
	"strconv"
)

func solve(${formal_arguments}) {

}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	const initialBufSize = 4096
	const maxBufSize = 1000000
	scanner.Buffer(make([]byte, initialBufSize), maxBufSize)
	scanner.Split(bufio.ScanWords)
	${input_part}
	solve(${actual_arguments})
}
