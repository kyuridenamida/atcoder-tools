#include <bits/stdc++.h>
using namespace std;

void solve(long long H, long long W, long long N, vector<long long> X, vector<long long> Y){

}

int main(){
    long long H;
    scanf("%lld",&H);
    long long W;
    scanf("%lld",&W);
    long long N;
    scanf("%lld",&N);
    vector<long long> X(N-1+1);
    vector<long long> Y(N-1+1);
    for(int i = 0 ; i <= N-1 ; i++){
        scanf("%lld",&X[i]);
        scanf("%lld",&Y[i]);
    }
    solve(H, W, N, X, Y);
    return 0;
}
