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
	const initialBufSize = 4096
	const maxBufSize = 1000000
	scanner.Buffer(make([]byte, initialBufSize), maxBufSize)
	scanner.Split(bufio.ScanWords)
{% if multi_case %}
	{{ prefix_input_part }}
	for {{ case_loop_var }} := int64(0); {{ case_loop_var }} < {{ case_count_var }}; {{ case_loop_var }}++ {
		{{ case_input_part | replace('\n', '\n' ~ "\t") }}
		solve({{ actual_arguments }})
	}
{% else %}
	{{ input_part }}
	solve({{ actual_arguments }})
{% endif %}
	{% else %}
    // Failed to predict input format
	{% endif %}
}
