package main
{% if prediction_success %}

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strconv"
)
{% endif %}
{% if mod or yes_str or no_str %}

{% endif %}
{% if mod %}
const MOD = {{mod}}
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
	if int64(len(H)) != N-1 {
		log.Fatal()
	}
	for i := int64(0); i < N-1; i++ {
		if int64(len(H[i])) != M-2 {
			log.Fatal()
		}
		for j := int64(0); j < M-2; j++ {
			if j > 0 {
				fmt.Printf(" %s", H[i][j])
			} else {
				fmt.Printf("%s", H[i][j])
			}
		}
		fmt.Println()
	}

	if int64(len(A)) != N-1 {
		log.Fatal()
	}
	if int64(len(B)) != N-1 {
		log.Fatal()
	}
	for i := int64(0); i < N-1; i++ {
		fmt.Printf("%d %.1f\n", A[i], B[i])
	}

	fmt.Println(Q)
	if int64(len(X)) != M+Q {
		log.Fatal()
	}
	for i := int64(0); i < M+Q; i++ {
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
	scanner.Split(bufio.ScanWords)
	{{ input_part }}
	solve({{ actual_arguments }})
	{% else %}
    // Failed to predict input format
	{% endif %}
}
