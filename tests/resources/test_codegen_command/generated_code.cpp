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

void solve(long long N, long long M, std::vector<long long> a, std::vector<long long> b, std::vector<long long> t){

}
int main(){
    long long N;
    scanf("%lld", &N);
    long long M;
    scanf("%lld", &M);
    std::vector<long long> a(M);
    std::vector<long long> b(M);
    std::vector<long long> t(M);
    for(int i = 0 ; i < M ; i++){
        scanf("%lld", &a[i]);
        scanf("%lld", &b[i]);
        scanf("%lld", &t[i]);
    }
    solve(N, M, std::move(a), std::move(b), std::move(t));
    return 0;
}
