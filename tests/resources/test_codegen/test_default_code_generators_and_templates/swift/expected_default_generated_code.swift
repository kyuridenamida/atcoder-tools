import Foundation

let MOD = 123
let YES = "yes"
let NO = "NO"

func solve(_ N:Int, _ M:Int, _ H:[[String]], _ A:[Int], _ B:[Double], _ Q:Int, _ X:[Int]) {
    var ans = false

    print(ans ? YES : NO)
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
    solve(N, M, H, A, B, Q, X)
}

#if DEBUG
let caseNumber = 1
_ = freopen("in_\(caseNumber).txt", "r", stdin)
#endif

main()
