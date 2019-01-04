import java.io.*;
import java.util.*;

class Main {
	{% if mod %static final long MOD = {{ mod }};{% endif %}
	{% if yes_str is not none %}static final String YES = "{{ yes_str }}";{% endif %}
	{% if no_str is not none %}static final String NO = "{{ no_str }}";{% endif %}

	public static void main(String[] args) throws Exception {
		final Scanner sc = new Scanner(System.in);
		{{ input_part }}
		solve({{ actual_arguments }});
	}

	static void solve({{ formal_arguments }}){

	}
}
