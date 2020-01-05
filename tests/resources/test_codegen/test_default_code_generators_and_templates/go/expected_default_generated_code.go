package main

import (
	"bufio"
	"os"
	"strconv"
)

const MOD = 123
const YES = "yes"
const NO = "NO"

func solve(N int64, M int64, H [][]string, A []int64, B []float64, Q int64, X []int64) {

}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	const initialBufSize = 4096
	const maxBufSize = 1000000
	scanner.Buffer(make([]byte, initialBufSize), maxBufSize)
	scanner.Split(bufio.ScanWords)
	var N int64
	scanner.Scan()
	N, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	var M int64
	scanner.Scan()
	M, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	H := make([][]string, N-2+1)
	for i := int64(0); i < N-2+1; i++ {
		H[i] = make([]string, M-1-2+1)
	}
	for i := int64(0); i < N-2+1; i++ {
		for j := int64(0); j < M-1-2+1; j++ {
			scanner.Scan()
			H[i][j] = scanner.Text()
		}
	}
	A := make([]int64, N-2+1)
	B := make([]float64, N-2+1)
	for i := int64(0); i < N-2+1; i++ {
		scanner.Scan()
		A[i], _ = strconv.ParseInt(scanner.Text(), 10, 64)
		scanner.Scan()
		B[i], _ = strconv.ParseFloat(scanner.Text(), 64)
	}
	var Q int64
	scanner.Scan()
	Q, _ = strconv.ParseInt(scanner.Text(), 10, 64)
	X := make([]int64, M+Q)
	for i := int64(0); i < M+Q; i++ {
		scanner.Scan()
		X[i], _ = strconv.ParseInt(scanner.Text(), 10, 64)
	}
	solve(N, M, H, A, B, Q, X)
}
