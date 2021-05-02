#include<bits/stdc++.h>

using namespace std;

using Int = long long;

#define REP(i,n) for(int i=0;i<(int)(n);++i)

Int pow10_Int(Int a){
	Int ret = 1;
	REP(i,a)ret *= 10;
	return ret;
}

int main(){
	char result;
	const Int N = pow10_Int(10);
	cout<<"? "<<N<<endl;
	cin>>result;
	if(result=='Y'){//N = 10^t
		Int t = 0;
		for(int l = 1;l<=10;l++){
			t*=10;t+=9;
			cout<<"? "<<t<<endl;
			cin>>result;
			if(result=='Y'){
				int t = l - 1;
				cout<<"! "<<pow10_Int(t)<<endl;
				break;
			}
		}
		return 0;
	}
	int d = -1;
	for(int i = 1;i<=10;i++){
		cout<<"? "<<pow10_Int(i)<<endl;
		cin>>result;
		if(result=='N'){
			d = i;
			break;
		}
	}
	assert(d>=0);
	// # of digits is d
	Int l = pow10_Int(d-1), r = pow10_Int(d);
	while(r-l>1){
		Int m = (l+r)/2;
		cout<<"? "<<m*10<<endl;
		cin>>result;
		if(result=='Y'){
			r = m;
		}else{
			l = m;
		}
	}
	assert(r == l + 1);
	cout<<"! "<<r<<endl;
	return 0;
}
