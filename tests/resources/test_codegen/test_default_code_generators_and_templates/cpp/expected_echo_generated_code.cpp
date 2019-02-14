#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

const int mod = 123;
const string YES = "yes";
const string NO = "NO";
void solve(long long N, long long M, std::vector<std::vector<std::string>> H, std::vector<long long> A, std::vector<long double> B, long long Q, std::vector<long long> X){
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
    long long N;
    scanf("%lld",&N);
    long long M;
    scanf("%lld",&M);
    std::vector<std::vector<std::string>> H(N-2+1, std::vector<std::string>(M-1-2+1));
    for(int i = 0 ; i < N-2+1 ; i++){
        for(int j = 0 ; j < M-1-2+1 ; j++){
            std::cin >> H[i][j];
        }
    }
    std::vector<long long> A(N-2+1);
    std::vector<long double> B(N-2+1);
    for(int i = 0 ; i < N-2+1 ; i++){
        scanf("%lld",&A[i]);
        scanf("%Lf",&B[i]);
    }
    long long Q;
    scanf("%lld",&Q);
    std::vector<long long> X(M+Q);
    for(int i = 0 ; i < M+Q ; i++){
        scanf("%lld",&X[i]);
    }
    solve(N, M, std::move(H), std::move(A), std::move(B), Q, std::move(X));
    return 0;
}
