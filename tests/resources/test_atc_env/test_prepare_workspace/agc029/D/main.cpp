#include<iostream>
#include<vector>
#include<string>

void solve(long long H, long long W, long long N, std::vector<long long> X, std::vector<long long> Y){

}

int main(){
    long long H;
    std::cin >> H;
    long long W;
    std::cin >> W;
    long long N;
    std::cin >> N;
    std::vector<long long> X(N);
    std::vector<long long> Y(N);
    for(int i = 0 ; i < N ; i++){
        std::cin >> X[i];
        std::cin >> Y[i];
    }
    solve(H, W, N, std::move(X), std::move(Y));
    return 0;
}
