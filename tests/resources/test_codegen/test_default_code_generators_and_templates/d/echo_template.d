import std.algorithm;
import std.conv;
import std.stdio;
import std.string;
{% if mod or yes_str or no_str %}

{% endif %}
{% if mod %}
immutable long MOD = {{ mod }};
{% endif %}
{% if yes_str %}
immutable string YES = "{{ yes_str }}";
{% endif %}
{% if no_str %}
immutable string NO = "{{ no_str }}";
{% endif %}
{% if prediction_success %}

void solve({{ formal_arguments }}){
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

{% endif %}
int main(){
    {% if prediction_success %}
    {{ input_part }}
    solve({{ actual_arguments }});
    {% endif %}
    return 0;
}
