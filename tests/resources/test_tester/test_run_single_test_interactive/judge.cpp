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

///////////////////end template

typedef long long Int;

int main(int argc, char *argv[]){
	//////////////// start template
	cerr<<header_prefix<<endl;
	ifstream in_s_2(argv[1]);
	while(in_s_2){
		string s;
		getline(in_s_2,s);
		cout<<s<<endl;
		cerr<<s<<endl;
	}
	ifstream in_s(argv[1]), out_s(argv[2]);
	//////////////// end template
	string sN;
	out_s >> sN;
	Int N = atoll(sN.c_str());
	int ct = 0;
	while(1){
		string line = input();
		stringstream ss(line);
		char q;
		ss>>q;
		if(q=='?'){
			ct++;
			if(ct>64)quitWA("too many queries");
			string sn;
			ss>>sn;
			Int n = atoll(sn.c_str());
			if((n <= N and sn <= sN) or (n > N and sn > sN))output("Y");
			else output("N");
		}else if(q=='!'){
			Int n;
			ss>>n;
			if(n == N){
				quitAC();
			}else{
				quitWA("incorrect output");
			}
		}else{
			quitWA("invalid query");
		}
	}
}

