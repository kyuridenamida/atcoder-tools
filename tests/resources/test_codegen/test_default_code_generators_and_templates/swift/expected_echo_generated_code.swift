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
    var tokenIndex = 0
    var tokenBuffer = [String]()
    func nextToken() -> String {
        if tokenIndex >= tokenBuffer.count {
            tokenIndex = 0
            tokenBuffer = readLine()!.split(separator: " ").map { String($0) }
        }
        tokenIndex += 1
        return tokenBuffer[tokenIndex - 1]
    }
    let N = Int(nextToken())!
    let M = Int(nextToken())!
    var H = [[String]]()
    for i in 0..<N-2+1 {
        H.append([String]())
        for _ in 0..<M-1-2+1 {
            H[i].append(nextToken())
        }
    }
    var A = [Int]()
    var B = [Double]()
    for _ in 0..<N-2+1 {
        A.append(Int(nextToken())!)
        B.append(Double(nextToken())!)
    }
    let Q = Int(nextToken())!
    var X = [Int]()
    for _ in 0..<M+Q {
        X.append(Int(nextToken())!)
    }
    _ = solve(N, M, H, A, B, Q, X)
}

main()
