import std.algorithm;
import std.conv;
import std.stdio;
import std.string;

void solve(${formal_arguments}){

}

int main(){
    auto input = stdin.byLine.map!split.joiner;

    ${input_part}
    solve(${actual_arguments});
    return 0;
}
