#include <bits/stdc++.h>
using namespace std;

void solve(long long N, long long start, long long goal, vector<long long> l, vector<long long> r){
    
}

int main(){    
    long long N;
    scanf("%lld",&N);
    long long start;
    scanf("%lld",&start);
    long long goal;
    scanf("%lld",&goal);
    vector<long long> l(N-0+1);
    vector<long long> r(N-0+1);
    for(int i = 0 ; i <= N-0 ; i++){
        scanf("%lld",&l[i]);
        scanf("%lld",&r[i]);
    }
    solve(N, start, goal, l, r);
    return 0;
}

