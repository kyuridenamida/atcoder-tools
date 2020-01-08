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
  discard

proc main():void =
  var N:int
  N = nextInt()
  var M:int
  M = nextInt()
  var H = newSeqWith(N-2+1, newSeqWith(M-1-2+1, nextString()))
  var A = newSeqWith(N-2+1, 0)
  var B = newSeqWith(N-2+1, 0.0)
  for i in 0..<N-2+1:
    A[i] = nextInt()
    B[i] = nextFloat()
  var Q:int
  Q = nextInt()
  var X = newSeqWith(M+Q, nextInt())
  solve(N, M, H, A, B, Q, X)
  return

main()
