#include<iostream>
#include<vector>
#include<string>

{% if mod is not none %}
const int mod = {{ mod }};
{% endif %}
{% if yes_str is not none %}
const std::string YES = "{{ yes_str }}";
{% endif %}
{% if no_str is not none %}
const std::string NO = "{{ no_str }}";
{% endif %}
void solve({{ formal_arguments }}){

}
int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
