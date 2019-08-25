using System;
using System.Text;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using static System.Console;
using static System.Math;
using System.Diagnostics;

public class Program{
    const long MOD = 123;
    const string YES = "yes";
    const string NO = "NO";

    public static void Main(string[] args){
        ConsoleInput cin = new ConsoleInput(Console.In, ' ');
        long N;
        N = cin.ReadLong;
        long M;
        M = cin.ReadLong;
        string[,] H = new string[N-2+1,M-1-2+1];
        for(int i = 0;i < N-2+1;i++){
            for(int j = 0;j < M-1-2+1;j++){
                H[i,j] = cin.Read;
            }
        }
        long[] A = new long[N-2+1];
        double[] B = new double[N-2+1];
        for(int i = 0;i < N-2+1;i++){
            A[i] = cin.ReadLong;
            B[i] = cin.ReadDouble;
        }
        long Q;
        Q = cin.ReadLong;
        long[] X = new long[M+Q];
        for(int i = 0;i < M+Q;i++){
            X[i] = cin.ReadLong;
        }
        new Program().Solve(N, M, H, A, B, Q, X);
    }

    public void Solve(long N, long M, string[,] H, long[] A, double[] B, long Q, long[] X){
        WriteLine($"{N} {M}");
        Debug.Assert(H.GetLength(0) == N - 1);
        for (int i = 0;i < N - 1;i++) {
            Debug.Assert(H.GetLength(1) == M - 2);
            for (int j = 0;j < M - 2;j++) {
                Write((j > 0 ? " " : "") + $"{H[i,j]}");
            }
            WriteLine();
        }
        Debug.Assert(A.Length == N - 1);
        Debug.Assert(B.Length == N - 1);
        for(int i = 0;i < N - 1;i++){
            WriteLine($"{A[i]} {B[i]}");
        }
        WriteLine(Q);
        Debug.Assert(X.Length == M + Q);
        for(int i = 0;i < M + Q;i++){
            WriteLine(X[i]);
        }

        WriteLine(YES);
        WriteLine(NO);
        WriteLine(MOD);

    }
}

public class ConsoleInput{
    private readonly System.IO.TextReader _stream;
    private char _separator = ' ';
    private Queue<string> inputStream;
    public ConsoleInput(System.IO.TextReader stream, char separator = ' '){
        this._separator = separator;
        this._stream = stream;
        inputStream = new Queue<string>();
    }
    public string Read{
        get{
            if (inputStream.Count != 0) return inputStream.Dequeue();
            string[] tmp = _stream.ReadLine().Split(_separator);
            for (int i = 0; i < tmp.Length; ++i)
                inputStream.Enqueue(tmp[i]);
            return inputStream.Dequeue();
        }
    }
    public string ReadLine { get { return _stream.ReadLine(); } }
    public int ReadInt { get { return int.Parse(Read); } }
    public long ReadLong { get { return long.Parse(Read); } }
    public double ReadDouble { get { return double.Parse(Read); } }
    public string[] ReadStrArray(long N) { var ret = new string[N]; for (long i = 0; i < N; ++i) ret[i] = Read; return ret;}
    public int[] ReadIntArray(long N) { var ret = new int[N]; for (long i = 0; i < N; ++i) ret[i] = ReadInt; return ret;}
    public long[] ReadLongArray(long N) { var ret = new long[N]; for (long i = 0; i < N; ++i) ret[i] = ReadLong; return ret;}
}
