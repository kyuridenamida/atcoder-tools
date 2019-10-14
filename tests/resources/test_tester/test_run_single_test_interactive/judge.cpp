#include<bits/stdc++.h>

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

int main(int argc, char *argv[]){
	cerr<<header_prefix<<endl;
	ifstream in_s_2(argv[1]);
	while(in_s_2){
		string s;
		getline(in_s_2,s);
		cout<<s<<endl;
		cerr<<s<<endl;
	}
	ifstream in_s(argv[1]), out_s(argv[2]);
	int N, Q;
	string ans, str;
	in_s>>N>>Q;
	out_s>>ans;
	for(int ct = 0;;){
		str = input();
		stringstream ss(str);
		string type;
		ss>>type;
		if(type=="?"){
			ct++;
			if(ct > Q)quitWA("too many queries");
			char p, q;
			ss>>p>>q;
			if(not ('A' <= p and p < 'A' + N))quitWA("invalid query");
			if(not ('A' <= q and q < 'A' + N))quitWA("invalid query");
			int i = ans.find(p), j = ans.find(q);
			if(i < j){
				output("<");
			}else{
				output(">");
			}
		}else if(type=="!"){
			string out;
			ss>>out;
			if(ans == out){
				quitAC();
			}else{
				quitWA("wrong output");
			}
		}else{
			quitWA("invalid type");
		}
	}
}
