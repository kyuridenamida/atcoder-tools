import Foundation

{% if mod is not none %}
let MOD = {{ mod }}
{% endif %}
{% if yes_str is not none %}
let YES = "{{ yes_str }}"
{% endif %}
{% if no_str is not none %}
let NO = "{{ no_str }}"
{% endif %}

func solve({{ formal_arguments }}) -> Bool {
    print("\(N) \(M)")
    guard H.count == N - 1 else {
        return false
    }
    for i in 0..<N-1 {
        guard H[i].count == M - 2 else {
            return false
        }
        for j in 0..<M-2 {
            if j > 0 {
                print(" ", terminator: "")
            }
            print("\(H[i][j])", terminator: "")
        }
        print("")
    }
    guard A.count == N - 1, B.count == N - 1 else {
        return false
    }
    for i in 0..<N-1 {
        print("\(A[i]) \(B[i])")
    }
    print("\(Q)")
    guard X.count == M + Q else {
        return false
    }
    for i in 0..<M + Q {
        print("\(X[i])")
    }

    print(YES)
    print(NO)
    print(MOD)

    return true
}

func main() {
    var tokenIndex = 0, tokenBuffer = [String]()
    func readString() -> String {
        if tokenIndex >= tokenBuffer.count {
            tokenIndex = 0
            tokenBuffer = readLine()!.split(separator: " ").map { String($0) }
        }
        defer { tokenIndex += 1 }
        return tokenBuffer[tokenIndex]
    }
    func readInt() -> Int { Int(readString())! }
    func readDouble() -> Double { Double(readString())! }
    {{input_part}}
    _ = solve({{ actual_arguments }})
}

main()
