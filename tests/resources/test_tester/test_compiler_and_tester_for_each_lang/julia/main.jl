#!/usr/bin/env julia

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
    A = parse(Int, take!(tokens))
    B = parse(Int, take!(tokens))
    C = parse(Int, take!(tokens))
    if A + B >= C
        println("Yes")
    else
        println("No")
    end
end

isempty(ARGS) && main()
