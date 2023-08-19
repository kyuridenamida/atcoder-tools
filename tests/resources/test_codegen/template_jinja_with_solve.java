import java.io.*;
import java.util.*;

class Main {
    {% if mod is not none %}
    static final int mod = {{ mod }};
    {% endif %}
    {% if yes_str is not none %}
    static final String YES = "{{ yes_str }}";
    {% endif %}
    {% if no_str is not none %}
    static final String NO = "{{ no_str }}";
    {% endif %}
    public static void main(String[] args) throws Exception {
        {{ input_part_with_solve_function }}
    }

    static void solve({{ formal_arguments }}){

    }
}
