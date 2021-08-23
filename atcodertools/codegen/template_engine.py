import re
import string
import warnings

from jinja2 import Environment

from atcodertools.release_management.version import __version__


def _substitute(s, reps):
    # http://stackoverflow.com/questions/36739667/python-templates-for-generating-python-code-with-proper-multiline-indentation
    t = string.Template(s)
    i = 0
    cr = {}  # fileutils to iterate through the pattern string
    while True:
        # search for next replaceable token and its prefix
        m = re.search(r'^(.*?)\$\{(.*?)\}', s[i:], re.MULTILINE)

        if m is None:
            break  # no more : finished
        # the list is joined using the prefix if it contains only blanks
        sep = ('\n' + m.group(1)) if m.group(1).strip() == '' else '\n'

        cr[m.group(2)] = sep.join(reps[m.group(2)])
        i += m.end()  # continue past last processed replaceable token
    return t.substitute(cr)  # we can now substitute


def render(template, **kwargs):
    # TODO: refactoring: this should not be here.
    # TODO: refactoring: the URL should be imported from other module
    kwargs['atcodertools'] = {
        'version': __version__,
        'url': 'https://github.com/kyuridenamida/atcoder-tools',
    }

    # Fix the ident of template
    # TODO: refactoring: this should not be here.
    indent_template = estimate_indent(template)
    if indent_template and 'config' in kwargs:
        # Successfully estimated the indents of template
        indent = kwargs['config'].indent(1)
        if indent_template != indent:
            # Align the indent of template with kwargs
            def fixindent(line):
                new_indent = ''
                while line.startswith(indent_template):
                    line = line[len(indent_template):]
                    new_indent = new_indent + indent
                return new_indent + line
            template = '\n'.join(map(fixindent, template.split('\n')))

    if "${" in template:
        # If the template is old, render with the old engine.
        # This logic is for backward compatibility
        warnings.warn(
            "The old template engine with ${} is deprecated. Please use the new Jinja2 template engine.", UserWarning)

        return old_render(template, **kwargs)
    else:
        return render_by_jinja(template, **kwargs)


def old_render(template, **kwargs):
    # This render function used to be used before version 1.0.3
    new_args = {}

    for k, v in kwargs.items():
        new_args[k] = v if isinstance(v, list) else [v]

    return _substitute(template, new_args)


def render_by_jinja(template, **kwargs):
    return Environment(trim_blocks=True,
                       lstrip_blocks=True).from_string(template).render(**kwargs) + "\n"


def estimate_indent(code):
    indents = re.findall(r'^([ \t]+)(?=\S)', code, re.MULTILINE)
    if not indents:
        return ''
    indents_concat = "".join(indents)
    if ' ' in indents_concat and '\t' in indents_concat:
        return ''
    lens = set([len(indent) for indent in indents])
    if not min(lens) * len(lens) == max(lens):
        return ''
    return indents[0][:min(lens)]
