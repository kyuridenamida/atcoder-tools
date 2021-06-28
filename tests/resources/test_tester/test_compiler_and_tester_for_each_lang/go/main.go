package main

import (
	"bufio"
	"os"
	"strconv"
	"fmt"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	const initialBufSize = 4096
	const maxBufSize = 1000000
	scanner.Buffer(make([]byte, initialBufSize), maxBufSize)
	scanner.Split(bufio.ScanWords)
	
	var A, B, C int64
	scanner.Scan()
	A, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	scanner.Scan()
	B, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	scanner.Scan()
	C, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	if A + B >= C {
		fmt.Print("Yes\n")
	}else{
		fmt.Print("No\n")
	}
}
