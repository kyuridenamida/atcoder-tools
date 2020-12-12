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
    func readInt() -> Int { readInt() }
    func readDouble() -> Double { readDouble() }
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
    solve(N, M, H, A, B, Q, X)
}

#if DEBUG
let caseNumber = 1
_ = freopen("in_\(caseNumber).txt", "r", stdin)
#endif

main()
