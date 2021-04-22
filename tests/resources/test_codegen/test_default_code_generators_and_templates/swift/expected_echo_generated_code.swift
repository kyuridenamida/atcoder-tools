import Foundation

let MOD = 123
let YES = "yes"
let NO = "NO"

func solve(_ N:Int, _ M:Int, _ H:[[String]], _ A:[Int], _ B:[Double], _ Q:Int, _ X:[Int]) -> Bool {
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
    let N = readInt()
    let M = readInt()
    var H = [[String]]()
    for i in 0..<N-2+1 {
        H.append([String]())
        for _ in 0..<M-1-2+1 {
            H[i].append(readString())
        }
    }
    var A = [Int]()
    var B = [Double]()
    for _ in 0..<N-2+1 {
        A.append(readInt())
        B.append(readDouble())
    }
    let Q = readInt()
    var X = [Int]()
    for _ in 0..<M+Q {
        X.append(readInt())
    }
    _ = solve(N, M, H, A, B, Q, X)
}

main()
