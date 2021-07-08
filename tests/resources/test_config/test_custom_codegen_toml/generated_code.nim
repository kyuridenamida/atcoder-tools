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

proc solve(H:int, W:int, c:seq[seq[int]], A:seq[seq[int]]):void =
  return

proc main():void =
  var H = nextKyuridenamida()
  var W = nextKyuridenamida()
  var c = Kyuridenamida(9+1, Kyuridenamida(9+1, nextKyuridenamida()))
  var A = Kyuridenamida(H, Kyuridenamida(W, nextKyuridenamida()))
  solve(H, W, c, A)
  return

main()
