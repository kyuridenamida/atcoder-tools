import std.algorithm;
import std.conv;
import std.stdio;
import std.string;

int main(){
	auto input = stdin.byLine.map!split.joiner;

	long A;
	A = input.front.to!long;
	input.popFront;

	long B;
	B = input.front.to!long;
	input.popFront;

	long C;
	C = input.front.to!long;
	input.popFront;

	if(A + B >= C)writeln("Yes");
	else writeln("No");
	return 0;
}
