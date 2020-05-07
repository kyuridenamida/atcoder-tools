#!/usr/bin/env julia
{% if prediction_success %}
{% endif %}
{% if mod or yes_str or no_str %}
{% endif %}
{% if mod %}
const MOD = {{ mod }}
{% endif %}
{% if yes_str %}
const YES = "{{ yes_str }}"
{% endif %}
{% if no_str %}
const NO = "{{ no_str }}"
{% endif %}
{% if prediction_success %}

function solve({{ formal_arguments }})
    println("$N $M")
    @assert size(H) == (N-1, M-2)
    for i in 1:size(H,1)
        println(join(H[i, :], " "))
    end
    @assert length(A) == N - 1
    @assert length(B) == N - 1
    for (a, b) in zip(A, B)
        println("$a $b")
    end
    println(Q)
    @assert length(X) == M + Q
    foreach(println, X)

    println(YES)
    println(NO)
    println(MOD)
end
{% endif %}


function main()
    tokens = Channel{String}(32)
    Task() do
        for line in eachline(@static VERSION < v"0.6" ? STDIN : stdin)
            for token in split(chomp(line))
                put!(tokens, token)
            end
        end
        close(tokens)
    end |> schedule
    {{ input_part }}
    solve({{ actual_arguments }})
end

isempty(ARGS) && main()
