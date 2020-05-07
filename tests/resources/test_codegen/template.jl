#!/usr/bin/env julia

function solve(${formal_arguments})
  
end

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
    ${input_part}
    solve(${actual_arguments})
end

isempty(ARGS) && main()
