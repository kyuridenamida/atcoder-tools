#include <bits/stdc++.h>
using namespace std;

#define REP(i,n) for(int i=0;i<(int)(n);++i)

typedef long long Int;

Int N;
vector<Int> Y;
vector<Int> X;

pair<Int,Int> simulate(vector<Int> &v, const string &s){
	Int X=0,Y=0;
	REP(i,v.size()){
		if(s[i]=='L')X-=v[i];
		else if(s[i]=='R')X+=v[i];
		else if(s[i]=='D')Y-=v[i];
		else if(s[i]=='U')Y+=v[i];
		else assert(false);
	}
	return {X,Y};
}

void solve(){
	vector<bool> parity = {false,false};
	REP(i,N){
		parity[((X[i]+Y[i])%2+2)%2] = true;
	}
	if(parity[0] and parity[1]){
		cout<<-1<<endl;
		return;
	}
	bool opt = false;
	if(parity[0]){
		opt = true;
	}
	vector<Int> v;
	int m = 39;
	cout<<m + opt<<endl;
	if(opt)v.push_back(1);
	REP(i,m)v.push_back(1ll<<i);
	REP(i,v.size()){
		cout<<v[i]<<" ";
	}
	cout<<endl;
	REP(i,N){
		string s;
		if(opt){
			s+="L";
			X[i]++;
		}
		REP(j,m){
			bool swp = false;
			if(X[i]%2!=0){
				swp = true;
				swap(X[i],Y[i]);
			}
			assert(X[i]%2==0);
			assert(Y[i]%2!=0);
			if(j==m-1){
				if(Y[i]==-1){
					s+=((!swp)?'D':'L');
				}else if(Y[i]==1){
					s+=((!swp)?'U':'R');
				}else{
					assert(false);
				}
			}else{
				X[i]/=2;
				int d = (Y[i]+1)/2, u = (Y[i]-1)/2;
				if(X[i]%2==0){
					if(d%2!=0){
						s+=((!swp)?'D':'L');
						Y[i] = d;
					}else{
						s+=((!swp)?'U':'R');
						Y[i] = u;
					}
				}else{
					if(d%2==0){
						s+=((!swp)?'D':'L');
						Y[i] = d;
					}else{
						s+=((!swp)?'U':'R');
						Y[i] = u;
					}
				}
				if(swp)swap(X[i],Y[i]);
			}
		}
		cout<<s<<endl;
	}
}

int main(){	

	cin >> N;
	Y.assign(N-1+1,Int());
	X.assign(N-1+1,Int());
	for(int i = 0 ; i <= N-1 ; i++){
		cin >> X[i];
		cin >> Y[i];
	}
	solve();
	return 0;
}
