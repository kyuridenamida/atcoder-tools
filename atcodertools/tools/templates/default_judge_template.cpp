#include <bits/stdc++.h>

using namespace std;

typedef long long Int;

void exit_ac(){
	cerr<<"Judge: AC"<<endl;
	exit(0);
}
void exit_wa(const string message = ""){
	cerr<<"Judge: WA"<<" ( "<<message<<" )"<<endl;
	exit(1);
}

#ifdef INTERACTIVE
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
#endif

typedef long long Int;

int main(int argc, char *argv[]){
#ifdef INTERACTIVE
	cerr<<header_prefix<<endl;
	ifstream in_s_2(argv[1]);
	while(in_s_2){
		string s;
		getline(in_s_2,s);
		cout<<s<<endl;
		cerr<<s<<endl;
	}
#endif
	ifstream in_s(argv[1]), out_s(argv[2]);
	//write code
	
	
	
	assert(false);
}
