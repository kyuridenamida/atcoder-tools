package main

import "fmt"

func main() {
	var A, B, C int
	fmt.Scan(&A, &B, &C)
	if A+B >= C {
		fmt.Println("Yes")
	} else {
		fmt.Println("No")
	}
}
