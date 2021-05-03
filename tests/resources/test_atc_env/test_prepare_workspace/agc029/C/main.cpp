#include<iostream>
#include<vector>
#include<string>

void solve(long long N, std::vector<long long> A){

}

int main(){
    long long N;
    scanf("%lld", &N);
    std::cin >> N;
    std::vector<long long> A(N);
    for(int i = 0 ; i < N ; i++){
        scanf("%lld", &A[i]);
    }
    solve(N, std::move(A));
    return 0;
}
