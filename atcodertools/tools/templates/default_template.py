#!/usr/bin/env python3
{% if prediction_success %}
import sys
{% endif %}

{% if mod %}
MOD = {{ mod }}  # type: int
{% endif %}
{% if yes_str %}
YES = "{{ yes_str }}"  # type: str
{% endif %}
{% if no_str %}
NO = "{{ no_str }}"  # type: str
{% endif %}

{% if prediction_success %}
def solve({{ formal_arguments }}):
    return

{% endif %}

def main():
    {% if prediction_success %}
    def iterate_tokens():
        for line in sys.stdin:
            for word in line.split():
                yield word
    tokens = iterate_tokens()
    {{ input_part }}
    solve({{ actual_arguments }})
    {% else %}
    # Failed to predict input format
    pass
    {% endif %}

if __name__ == '__main__':
    main()
