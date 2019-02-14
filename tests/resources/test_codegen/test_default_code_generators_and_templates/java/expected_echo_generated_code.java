import java.io.*;
import java.util.*;

class Main {
    static final long MOD = 123;
    static final String YES = "yes";
    static final String NO = "NO";

    public static void main(String[] args) throws Exception {
        final Scanner sc = new Scanner(System.in);
        long N;
        N = sc.nextLong();
        long M;
        M = sc.nextLong();
        String[][] H = new String[(int)(N-2+1)][(int)(M-1-2+1)];
        for(int i = 0 ; i < N-2+1 ; i++){
            for(int j = 0 ; j < M-1-2+1 ; j++){
                H[i][j] = sc.next();
            }
        }
        long[] A = new long[(int)(N-2+1)];
        double[] B = new double[(int)(N-2+1)];
        for(int i = 0 ; i < N-2+1 ; i++){
            A[i] = sc.nextLong();
            B[i] = sc.nextDouble();
        }
        long Q;
        Q = sc.nextLong();
        long[] X = new long[(int)(M+Q)];
        for(int i = 0 ; i < M+Q ; i++){
            X[i] = sc.nextLong();
        }
        solve(N, M, H, A, B, Q, X);
    }

    static void solve(long N, long M, String[][] H, long[] A, double[] B, long Q, long[] X){
        System.out.println("" + N + " " + M);
        assert H.length == N - 1;
        for(int i = 0 ; i < N - 1 ; i++){
            assert H[i].length == M - 2;
            for(int j = 0 ; j < M - 2 ; j++){
                if( j > 0 ) System.out.print(" ");
                System.out.print(H[i][j]);
            }
            System.out.println();
        }
        assert A.length == N - 1;
        assert B.length == N - 1;
        for(int i = 0 ; i < N - 1 ; i++){
            System.out.println("" + A[i] + " " + B[i]);
        }
        System.out.println(Q);
        assert X.length == M + Q;
        for(int i = 0 ; i < M + Q ; i++){
            System.out.println(X[i]);
        }
        System.out.println(YES);
        System.out.println(NO);
        System.out.println(MOD);
    }
}
