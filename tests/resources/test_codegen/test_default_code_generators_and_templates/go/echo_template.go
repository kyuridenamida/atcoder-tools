package main
{% if prediction_success %}

import (
	"bufio"
	"os"
	"strconv"
)
{% endif %}
{% if mod %}
const MOD = 1
{% endif %}
{% if yes_str %}
const YES = "{{ yes_str }}"
{% endif %}
{% if no_str %}
const NO = "{{ no_str }}"
{% endif %}
{% if prediction_success %}

func solve({{ formal_arguments }}) {
	fmt.Printf("%d %d\n", N, M)
	if len(H) != int(N-1) {
		log.Fatal()
	}
	for i := 0; i < int(N-1); i++ {
		if len(H[i]) != int(M-2) {
			log.Fatal()
		}
		for j := 0; j < int(M-2); j++ {
			if j > 0 {
				fmt.Printf(" %s", H[i][j])
			} else {
				fmt.Printf("%s", H[i][j])
			}
		}
		fmt.Println()
	}

	if len(A) != int(N-1) {
		log.Fatal()
	}
	if len(B) != int(N-1) {
		log.Fatal()
	}
	for i := 0; i < int(N-1); i++ {
		fmt.Printf("%d %f\n", A[i], B[i])
	}

	fmt.Println(Q)
	if len(X) != int(M)+int(Q) {
		log.Fatal()
	}
	for i := 0; i < int(N-1); i++ {
		fmt.Println(X[i])
	}

	fmt.Println(YES)
	fmt.Println(NO)
	fmt.Println(MOD)
}
{% endif %}

func main() {
	{% if prediction_success %}
	scanner := bufio.NewScanner(os.Stdin)
	{{ input_part }}
	solve({{ actual_arguments }})
	{% else %}
    // Failed to predict input format
	{% endif %}
}
