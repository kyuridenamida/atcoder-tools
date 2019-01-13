#include <bits/stdc++.h>
using namespace std;

{% if mod %}const long long MOD = {{ mod }};{% endif %}
{% if yes_str %}const string YES = "{{ yes_str }}";{% endif %}
{% if no_str %}const string NO = "{{ no_str }}";{% endif %}

void solve({{ formal_arguments }}){

}

int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
