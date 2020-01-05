package main
{% if prediction_success %}

import (
	"bufio"
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

}
{% endif %}

func main() {
	{% if prediction_success %}
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 1000000), 1000000)
	scanner.Split(bufio.ScanWords)
	{{ input_part }}
	solve({{ actual_arguments }})
	{% else %}
    // Failed to predict input format
	{% endif %}
}
