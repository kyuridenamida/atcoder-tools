/////////start template
#include <bits/stdc++.h>

using namespace std;

void quitAC(){
	cerr<<"Judge: AC"<<endl;
	exit(0);
}
void quitWA(const string message = ""){
	cerr<<"Judge: WA"<<" ( "<<message<<" )"<<endl;
	exit(1);
}
void Assert(bool b){
	if(not b)quitWA("assertion false");
}

#ifdef INTERACTIVE
///// only interactive
const string header_prefix = "Input                 Output\n----------------------------------";
const string input_prefix  = "                      ";

string input(){
	string s;
	getline(cin,s);
	cerr<<input_prefix<<s<<endl;
	return s;
}

void output(const string &s){
	cerr<<s<<endl;
	cout<<s<<endl;
}
///// end only interactive
#endif

///////////////////end template

typedef long long Int;

int main(int argc, char *argv[]){
	//////////////// start template
#ifdef INTERACTIVE
	///// only interactive
	cerr<<header_prefix<<endl;
	ifstream in_s_2(argv[1]);
	while(in_s_2){
		string s;
		getline(in_s_2,s);
		cout<<s<<endl;
		cerr<<s<<endl;
	}
	///// end only interactive
#endif
	ifstream in_s(argv[1]), out_s(argv[2]);
	//////////////// end template
	int N;
	in_s >> N;
	vector<Int> X(N), Y(N);
	for(int i = 0;i < N;i++){
		in_s>>X[i]>>Y[i];
	}
	
	int m_expected;
	out_s >> m_expected;
	int m;cin >> m;
	if(m_expected==-1){
		if(m==-1)quitAC();
		else quitWA("incorrect m");
	}
	vector<Int> d(m);
	for(int i = 0;i < m;i++)cin>>d[i];
	vector<string> w(N);
	for(int i = 0;i < N;i++)cin>>w[i];
	for(int i = 0;i < N;i++){
		Int x = 0, y = 0;
		int j = 0;
		Assert(w[i].size() == m);
		for(auto &&s:w[i]){
			switch(s){
			case 'L':x -= d[j];break;
			case 'R':x += d[j];break;
			case 'D':y -= d[j];break;
			case 'U':y += d[j];break;
			}
			j++;
		}
		if(not (x==X[i] and y == Y[i]))quitWA("incorrect output");
	}
	quitAC();
}

