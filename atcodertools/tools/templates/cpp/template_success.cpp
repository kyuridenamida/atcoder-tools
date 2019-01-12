#include <bits/stdc++.h>
using namespace std;

{% if mod is defined %}const long long MOD = {{ mod }};{% endif %}
{% if yes_str is defined %}const string YES = "{{ yes_str }}";{% endif %}
{% if no_str is defined %}const string NO = "{{ no_str }}";{% endif %}

void solve({{ formal_arguments }}){

}

int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
