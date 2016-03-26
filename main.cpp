#include <bits/stdc++.h>
using namespace std;





bool isVariableName(string a){
	for(int i = 0 ; i < a.size() ; i++)
		if( !( 'a' <= a[i] && a[i] <= 'z' ||  'A' <= a[i] && a[i] <= 'Z'  || a[i] == '_') ) return false;
	return true;
}
bool isDescription(string a){
	if( a.back() == '-') return false;
	if( a.find("_") != -1 ) return false;
	return true;
}
vector< vector<string> > devides(string text,map<string,int> vars){
	// 変数名に数字は含まれない　分割は3つまで考える
	vector< vector<string> > cand;
	cand.push_back({text});
	for(int i = 1 ; i < text.size() ; i++){
		cand.push_back({text.substr(0,i),text.substr(i)});
	}
	for(int i = 1 ; i < text.size() ; i++){
		for(int j = i+1 ; j < text.size() ; j++){
			cand.push_back({text.substr(0,i),text.substr(i,j-i),text.substr(j)});
		}
	}
	
	vector< vector<string> > res;
	for( auto c : cand ){
		bool f = 1;
		f &= isVariableName(c[0]);
		// cout << f << endl;
		for(int j = 1 ; j < c.size() ; j++){
			f &= isDescription(c[j]);
			if( isVariableName(c[j]) && !vars.count(c[j]) ) f = 0;  
		}
		if( vars.count(c[0]) && vars[c[0]] != c.size() ) f = 0;
		if(f){
			res.push_back(c);
		}
	}
	return res;
}


vector<string> token;

vector< vector<string> > ans;

vector< vector< vector<string> > > tmp;

bool dfs(int x,map<string,int> vars,int lim){
	if( lim < vars.size() ) return true;
	if( x == token.size() ){
		tmp.push_back(ans);
		return false;
	}
	auto divs = devides(token[x],vars);
	bool anss = 0;
	for( auto d : divs ){
		map<string,int> next = vars;
		next[d[0]] = d.size();
		ans.push_back(d);
		if( dfs(x+1,next,lim) ) anss = 1;
		ans.pop_back();
	}
	return anss;
}

vector< vector< vector<string> > > getParsed(){
	tmp.clear();
	for(int i = 1 ; ; i++){
		if( dfs(0,{},i) == false ) break;
		if( tmp.size() ) break;
	}
	return tmp;
}



int main(){
	string s;
	while( cin >> s ){
		token.push_back(s);
	}
	cout << getParsed().size() << endl;
	for( auto s : getParsed() ){
		for( auto t : s ){
			for( auto u : t )
				cout << u << " ";
			cout << endl;
		}
	}

}