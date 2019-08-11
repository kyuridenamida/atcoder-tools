import sequtils
proc scanf(formatstr: cstring){.header: "<stdio.h>", varargs.}
proc getchar(): char {.header: "<stdio.h>", varargs.}
proc nextInt(): int = scanf("%lld",addr result)
proc nextFloat(): float = scanf("%lf",addr result)
proc nextString(): string =
  var get = false
  result = ""
  while true:
    var c = getchar()
    if int(c) > int(' '):
      get = true
      result.add(c)
    else:
      if get: break
      get = false

{% if mod %}
let MOD = {{ mod }}
{% endif %}
{% if yes_str %}
let YES = "{{ yes_str }}"
{% endif %}
{% if no_str %}
let NO = "{{ no_str }}"
{% endif %}

proc solve({{ formal_arguments }}):void =
  echo N," ",M
  assert H.len == N - 1
  for i in 0..<N-1:
    assert H[i].len == M - 2
    for j in 0..<M-2:
      stdout.write if j > 0: " " else:"", H[i][j]
    echo ""
  assert A.len == N - 1
  assert B.len == N - 1
  for i in 0..<N-1:
    echo A[i]," ",B[i]
  echo Q
  assert X.len == M + Q
  for i in 0..<M + Q:
    echo X[i]
  echo YES
  echo NO
  echo MOD

proc main():void =
  {{input_part}}
  solve({{ actual_arguments }})
  return

main()
