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

{% if prediction_success %}
proc solve({{ formal_arguments }}):void =
  discard
{% endif %}

proc main():void =
{% if prediction_success %}
  {{input_part}}
  solve({{ actual_arguments }});
{% else %}
# Failed to predict input format
{% endif %}
  return

main()
