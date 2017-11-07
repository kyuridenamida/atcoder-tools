import string
import re


def substitute(s, reps):
    # http://stackoverflow.com/questions/36739667/python-templates-for-generating-python-code-with-proper-multiline-indentation
    t = string.Template(s)
    i = 0
    cr = {}  # prepare to iterate through the pattern string
    while True:
        # search for next replaceable token and its prefix
        m = re.search(r'^(.*?)\$\{(.*?)\}', s[i:], re.MULTILINE)

        if m is None:
            break  # no more : finished
        # the list is joined using the prefix if it contains only blanks
        sep = ('\n' + m.group(1)) if m.group(1).strip() == '' else '\n'

        cr[m.group(2)] = sep.join(reps[m.group(2)])
        i += m.end()   # continue past last processed replaceable token
    return t.substitute(cr)  # we can now substitute


def render(s, **args):
    new_args = {}

    for k, v in args.items():
        new_args[k] = v if isinstance(v, list) else [v]

    return substitute(s, new_args)
