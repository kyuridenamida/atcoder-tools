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

let MOD = 123
let YES = "yes"
let NO = "NO"

proc solve(N:int, M:int, H:seq[seq[string]], A:seq[int], B:seq[float], Q:int, X:seq[int]):void =
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
  var N = 0
  N = nextInt()
  var M = 0
  M = nextInt()
  var H = newSeqWith(N-2+1, newSeqWith(M-1-2+1, ""))
  for i in 0..<N-2+1:
    for j in 0..<M-1-2+1:
      H[i][j] = nextString()
  var A = newSeqWith(N-2+1, 0)
  var B = newSeqWith(N-2+1, 0.0)
  for i in 0..<N-2+1:
    A[i] = nextInt()
    B[i] = nextFloat()
  var Q = 0
  Q = nextInt()
  var X = newSeqWith(M+Q, 0)
  for i in 0..<M+Q:
    X[i] = nextInt()
  solve(N, M, H, A, B, Q, X)
  return

main()
