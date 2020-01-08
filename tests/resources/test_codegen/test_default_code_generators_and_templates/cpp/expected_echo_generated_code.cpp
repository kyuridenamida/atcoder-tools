#include <iostream>
#include <vector>
#include <string>
#include <cassert>

const int mod = 123;
const std::string YES = "yes";
const std::string NO = "NO";
void solve(long long N, long long M, std::vector<std::vector<std::string>> H, std::vector<long long> A, std::vector<long double> B, long long Q, std::vector<long long> X){
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
    long long N;
    std::cin >> N;
    long long M;
    std::cin >> M;
    std::vector<std::vector<std::string>> H(N-2+1, std::vector<std::string>(M-1-2+1));
    for(int i = 0 ; i < N-2+1 ; i++){
        for(int j = 0 ; j < M-1-2+1 ; j++){
            std::cin >> H[i][j];
        }
    }
    std::vector<long long> A(N-2+1);
    std::vector<long double> B(N-2+1);
    for(int i = 0 ; i < N-2+1 ; i++){
        std::cin >> A[i];
        std::cin >> B[i];
    }
    long long Q;
    std::cin >> Q;
    std::vector<long long> X(M+Q);
    for(int i = 0 ; i < M+Q ; i++){
        std::cin >> X[i];
    }
    solve(N, M, std::move(H), std::move(A), std::move(B), Q, std::move(X));
    return 0;
}
