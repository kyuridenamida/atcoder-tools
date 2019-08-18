import std.algorithm;
import std.conv;
import std.stdio;
import std.string;

immutable long MOD = 123;
immutable string YES = "yes";
immutable string NO = "NO";

void solve(long N, long M, string[][] H, long[] A, double[] B, long Q, long[] X){
    writeln(N.to!string ~ " " ~ M.to!string);
    assert(H.length == cast(size_t) (N - 1));
    foreach (i; 0 .. cast(size_t) (N - 1)) {
        assert(H[i].length == M - 2);
        writeln(H[i].join(" "));
    }
    assert(A.length == cast(size_t) (N - 1));
    assert(B.length == cast(size_t) (N - 1));
    foreach (i; 0 .. cast(size_t) (N - 1)) {
        writeln(A[i].to!string ~ " " ~ B[i].to!string);
    }
    writeln(Q);
    assert(X.length == cast(size_t) (M + Q));
    foreach (i; 0 .. cast(size_t) (M + Q)) {
        writeln(X[i]);
    }

    writeln(YES);
    writeln(NO);
    writeln(MOD);
}

int main(){
    auto input = stdin.byLine.map!split.joiner;

    long N;
    N = input.front.to!long;
    input.popFront;

    long M;
    M = input.front.to!long;
    input.popFront;

    string[][] H = new string[][](cast(size_t) (N-2+1), cast(size_t) (M-1-2+1));
    foreach (i; 0 .. cast(size_t) (N-2+1)) {
        foreach (j; 0 .. cast(size_t) (M-1-2+1)) {
            H[i][j] = input.front.to!string;
            input.popFront;
        }
    }

    long[] A = new long[](cast(size_t) (N-2+1));
    double[] B = new double[](cast(size_t) (N-2+1));
    foreach (i; 0 .. cast(size_t) (N-2+1)) {
        A[i] = input.front.to!long;
        input.popFront;
        B[i] = input.front.to!double;
        input.popFront;
    }

    long Q;
    Q = input.front.to!long;
    input.popFront;

    long[] X = new long[](cast(size_t) (M+Q));
    foreach (i; 0 .. cast(size_t) (M+Q)) {
        X[i] = input.front.to!long;
        input.popFront;
    }

    solve(N, M, H, A, B, Q, X);
    return 0;
}
