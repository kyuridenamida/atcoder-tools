import Foundation

{% if mod %}
let MOD = {{ mod }}
{% endif %}
{% if yes_str %}
let YES = "{{ yes_str }}"
{% endif %}
{% if no_str %}
let NO = "{{ no_str }}"
{% endif %}
{% if prediction_success %}

func solve({{ formal_arguments }}) {
    {% if yes_str %}
    var ans = false

    print(ans ? YES : NO)
    {% else %}
    var ans = 0

    print(ans)
    {% endif %}
}
{% endif %}

func main() {
    {% if prediction_success %}
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
    {{input_part}}
    solve({{ actual_arguments }})
    {% else %}
    // Failed to predict input format
    {% endif %}
}

#if DEBUG
let caseNumber = 1
_ = freopen("in_\(caseNumber).txt", "r", stdin)
#endif

main()
