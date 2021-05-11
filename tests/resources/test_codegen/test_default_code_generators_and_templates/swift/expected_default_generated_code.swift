import Foundation

let MOD = 123
let YES = "yes"
let NO = "NO"

func solve(_ N:Int, _ M:Int, _ H:[[String]], _ A:[Int], _ B:[Double], _ Q:Int, _ X:[Int]) {
    var ans = false

    print(ans ? YES : NO)
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
    var H = [[String]](repeating: [String](repeating: "", count: M-1-2+1), count: N-2+1)
    for i in 0..<N-2+1 {
        for j in 0..<M-1-2+1 {
            H[i][j] = readString()
        }
    }
    var A = [Int](repeating: 0, count: N-2+1)
    var B = [Double](repeating: 0.0, count: N-2+1)
    for i in 0..<N-2+1 {
        A[i] = readInt()
        B[i] = readDouble()
    }
    let Q = readInt()
    var X = [Int](repeating: 0, count: M+Q)
    for i in 0..<M+Q {
        X[i] = readInt()
    }
    _ = solve(N, M, H, A, B, Q, X)
}

#if DEBUG
let caseNumber = 1
_ = freopen("in_\(caseNumber).txt", "r", stdin)
#endif

main()
