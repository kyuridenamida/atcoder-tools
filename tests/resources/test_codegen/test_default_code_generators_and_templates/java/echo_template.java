import java.io.*;
import java.util.*;

class Main {
    {% if mod %}
    static final long MOD = {{ mod }};
    {% endif %}
    {% if yes_str %}
    static final String YES = "{{ yes_str }}";
    {% endif %}
    {% if no_str %}
    static final String NO = "{{ no_str }}";
    {% endif %}

    public static void main(String[] args) throws Exception {
        final Scanner sc = new Scanner(System.in);
        {% if prediction_success %}
        {{ input_part }}
        solve({{ actual_arguments }});
        {% else %}
        // Failed to predict input format
        {% endif %}
    }

    {% if prediction_success %}
    static void solve({{ formal_arguments }}){
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
    {% endif %}
}