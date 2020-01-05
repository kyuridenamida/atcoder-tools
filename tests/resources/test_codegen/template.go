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
	scanner.Buffer(make([]byte, 1000000), 1000000)
	scanner.Split(bufio.ScanWords)
	${input_part}
	solve(${actual_arguments})
}
