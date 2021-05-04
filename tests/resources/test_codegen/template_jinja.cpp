#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <deque>
#include <queue>
#include <stack>
#include <set>
#include <map>
#include <algorithm>
#include <functional>
#include <utility>
#include <bitset>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <cstdio>
#include <cassert>
using namespace std;

{% if mod is not none %}
const int mod = {{ mod }};
{% endif %}
{% if yes_str is not none %}
const string YES = "{{ yes_str }}";
{% endif %}
{% if no_str is not none %}
const string NO = "{{ no_str }}";
{% endif %}
void solve({{ formal_arguments }}){

}
int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
