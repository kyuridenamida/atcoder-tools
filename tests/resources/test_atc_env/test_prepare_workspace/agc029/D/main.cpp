#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <deque>
#include <queue>
#include <stack>
#include <set>
#include <map>
#include <algorithm>
#include <functional>
#include <utility>
#include <bitset>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <cstdio>
using namespace std;


void solve(long long H, long long W, long long N, std::vector<long long> X, std::vector<long long> Y){

}

int main(){
    long long H;
    scanf("%lld", &H);
    long long W;
    scanf("%lld", &W);
    long long N;
    scanf("%lld", &N);
    std::vector<long long> X(N);
    std::vector<long long> Y(N);
    for(int i = 0 ; i < N ; i++){
        scanf("%lld", &X[i]);
        scanf("%lld", &Y[i]);
    }
    solve(H, W, N, std::move(X), std::move(Y));
    return 0;
}
