#include <bits/stdc++.h>
using namespace std;

void solve(long long N, vector<long long> a, vector<long long> b){

}

int main(){
    long long N;
    scanf("%lld",&N);
    vector<long long> a(N-1);
    vector<long long> b(N-1);
    for(int i = 0 ; i < N-1 ; i++){
        scanf("%lld",&a[i]);
        scanf("%lld",&b[i]);
    }
    solve(N, a, b);
    return 0;
}
