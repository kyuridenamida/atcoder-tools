package main
{% if prediction_success %}

import (
	"bufio"
	"os"
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
