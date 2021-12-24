#include <iostream>
#include <unistd.h>

using namespace std;

int main(){
    int A, B, C;
    cin>>A>>B>>C;
    sleep(5);
    if(A + B >= C)cout<<"Yes"<<endl;
    else cout<<"No"<<endl;
    return 0;
}

