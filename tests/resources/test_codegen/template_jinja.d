{% if prediction_success %}
import std.algorithm;
import std.conv;
import std.stdio;
import std.string;
{% endif %}
{% if mod or yes_str or no_str %}

{% endif %}
{% if mod %}
immutable long MOD = {{ mod }};
{% endif %}
{% if yes_str %}
immutable string YES = "{{ yes_str }}";
{% endif %}
{% if no_str %}
immutable string NO = "{{ no_str }}";
{% endif %}
{% if prediction_success %}

void solve({{ formal_arguments }}){

}

{% endif %}
int main(){
    {% if prediction_success %}
    {{ input_part }}
    solve({{ actual_arguments }});
    {% else %}
    {% endif %}
    return 0;
}
