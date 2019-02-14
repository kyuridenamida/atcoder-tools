#include <iostream>
#include <vector>
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
    cout << N << " " << M << endl;
    assert(H.size() == N - 1);
    for (int i = 0; i < N - 1; i++) {
        assert(H[i].size() == M - 2);
        for (int j = 0; j < M - 2; j++) {
            cout << (j > 0 ? " " : "") << H[i][j];
        }
        cout << endl;
    }
    assert(A.size() == N - 1);
    assert(B.size() == N - 1);
    for(int i = 0 ; i < N - 1 ; i++){
        cout << A[i] << " " << B[i] << endl;
    }
    cout << Q << endl;
    assert(X.size() == M + Q);
    for(int i = 0 ; i < M + Q ; i++){
        cout << X[i] << endl;
    }

    cout << YES << endl;
    cout << NO << endl;
    cout << mod << endl;

}

int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
