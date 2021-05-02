#include<iostream>
#include<vector>
#include<string>

void solve(long long N, long long M, std::vector<long long> a, std::vector<long long> b, std::vector<long long> t){

}
int main(){
    long long N;
    std::cin >> N;
    long long M;
    std::cin >> M;
    std::vector<long long> a(M);
    std::vector<long long> b(M);
    std::vector<long long> t(M);
    for(int i = 0 ; i < M ; i++){
        std::cin >> a[i];
        std::cin >> b[i];
        std::cin >> t[i];
    }
    solve(N, M, std::move(a), std::move(b), std::move(t));
    return 0;
}
