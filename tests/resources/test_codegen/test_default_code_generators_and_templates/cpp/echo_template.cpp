#include <iostream>
#include <vector>
#include <string>
#include <cassert>

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
    std::cout << N << " " << M << std::endl;
    assert(H.size() == N - 1);
    for (int i = 0; i < N - 1; i++) {
        assert(H[i].size() == M - 2);
        for (int j = 0; j < M - 2; j++) {
            std::cout << (j > 0 ? " " : "") << H[i][j];
        }
        std::cout << std::endl;
    }
    assert(A.size() == N - 1);
    assert(B.size() == N - 1);
    for(int i = 0;i < N - 1;i++){
        std::cout << A[i] << " " << B[i] << std::endl;
    }
    std::cout << Q << std::endl;
    assert(X.size() == M + Q);
    for(int i = 0;i < M + Q;i++){
        std::cout << X[i] << std::endl;
    }

    std::cout << YES << std::endl;
    std::cout << NO << std::endl;
    std::cout << mod << std::endl;

}

int main(){
    {{input_part}}
    solve({{ actual_arguments }});
    return 0;
}
