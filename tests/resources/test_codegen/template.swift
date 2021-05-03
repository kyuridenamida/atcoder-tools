import Foundation

func solve({{ formal_arguments }}) {

}

func main() {
    func readString() -> String { "" }
    func readInt() -> Int { 0 }
    func readDouble() -> Double { 0 }
    {{input_part}}
    _ = solve({{ actual_arguments }})
}

main()
