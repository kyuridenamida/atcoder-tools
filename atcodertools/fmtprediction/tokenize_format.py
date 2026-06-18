import copy
import re
from typing import List, Dict

from atcodertools.fmtprediction.models.calculator import CalcNode, CalcParseError
from atcodertools.fmtprediction.models.variable_token import VariableToken, TokenizedFormat

from atcodertools.fmtprediction.token_manager import TokenManager


# --- String-grid collapse -------------------------------------------------
# A lot of problems describe a character grid (or a single string) by writing
# the same variable repeatedly with consecutive indices, e.g.
#     s_{1}s_{2}s_{3}            (a single string)
#     c_{11}c_{12}...c_{1W}      (one row of an H x W character grid)
# In the actual input, each such row is a single whitespace-delimited token
# (e.g. "*."), so the variable should be treated as a string and the
# fastest-varying index dimension should be collapsed away.
#
# We can't tell purely from the format text whether the cells are glued or
# space-separated (the notation is often inconsistent with the real data), so
# we generate a "collapsed" variant of the format text in addition to the
# original one and let the sample-based type prediction pick the valid one.

_REF = re.compile(r'([A-Za-z]+)(_\{[^{}]*\}|_\([^()]*\)|_[A-Za-z0-9])?')
_DOTS = re.compile(
    r'[ \t]*(?:\.\.\.\.|\.\.\.|\.\.|…|‥‥|‥|．．．|・・・・|・・・|ldots|cdots|dots)[ \t]*')
_SPACES = re.compile(r'[ \t]+')

# LaTeX commands used purely for spacing / dots in the format notation.
_LATEX_DOTS = ["\\ldots", "\\cdots", "\\dots", "\\vdots", "\\ddots"]
_LATEX_SPACES = ["\\,", "\\;", "\\:", "\\!", "\\quad", "\\qquad"]


def _normalize_separators(text: str) -> str:
    """Canonicalize the various ways a separator can be written so that the
    rest of the pipeline only has to deal with plain spaces (and ``…`` for
    the sequence indicator)."""
    for cmd in _LATEX_DOTS:
        text = text.replace(cmd, "…")
    for cmd in _LATEX_SPACES:
        text = text.replace(cmd, " ")
    # Remaining backslashes are LaTeX line breaks ("\\") / spacing ("\ ") and
    # carry no information for parsing.
    text = text.replace("\\", " ")
    # Full-width space is a regular separator.
    text = text.replace("　", " ")
    return text


def _strip_last_coord(name: str, idx) -> str:
    """Drop the trailing coordinate of a variable reference's index.

    c_{1,1} -> c_{1},  c_{11} -> c_{1},  s_{1} -> s,  c_{(0,1)} -> c_{0}
    """
    if idx is None:
        return name
    body = idx[1:]  # remove leading "_"
    if ((body.startswith('{') and body.endswith('}'))
            or (body.startswith('(') and body.endswith(')'))):
        inner = body[1:-1]
    else:
        inner = body
    if inner.startswith('(') and inner.endswith(')'):
        inner = inner[1:-1]

    if ',' in inner:
        coords = inner.split(',')[:-1]
        if not coords:
            return name
        return name + '_{' + ','.join(coords) + '}'
    if len(inner) <= 1:
        return name
    return name + '_{' + inner[:-1] + '}'


def _try_collapse_run(line: str, start: int):
    """Try to match a collapsible run of the same variable starting at start.

    A run is two or more references to the same variable name that are either
    glued together (no separator) or separated only by dots (a sequence
    indicator). Returns (collapsed_token, end_index) or None.
    """
    m = _REF.match(line, start)
    if not m or not m.group(1):
        return None
    name = m.group(1)
    first_idx = m.group(2)
    j = m.end()
    refs = 1
    glued = True
    saw_dots = False
    while True:
        k = j
        sep_has_dots = False
        sep_has_space = False
        progressed = True
        while progressed:
            progressed = False
            dm = _DOTS.match(line, k)
            if dm:
                sep_has_dots = True
                k = dm.end()
                progressed = True
                continue
            sm = _SPACES.match(line, k)
            if sm:
                sep_has_space = True
                k = sm.end()
                progressed = True
        m2 = _REF.match(line, k)
        if m2 and m2.group(0) and m2.group(1) == name:
            if sep_has_space:
                glued = False
            if sep_has_dots:
                saw_dots = True
            refs += 1
            j = m2.end()
        else:
            break

    if refs >= 2 and (glued or saw_dots):
        return _strip_last_coord(name, first_idx), j
    return None


# Underscore-less character strings such as "s1s2s3s4" or "c1c2...cN": a single
# letter followed by an index, repeated (glued or separated by dots) with the
# same letter. The trailing element may use a letter bound (e.g. "...cN").
_BARE_HEAD = re.compile(r'([A-Za-z])([0-9]+)')


def _try_bare_run(line: str, start: int):
    m = _BARE_HEAD.match(line, start)
    if not m:
        return None
    letter = m.group(1)
    j = m.end()
    refs = 1
    glued = True
    saw_dots = False
    esc = re.escape(letter)
    tail = re.compile(r'(?:' + esc + r'[0-9]+|' + esc + r'[A-Za-z])')
    while True:
        k = j
        sep_has_dots = False
        sep_has_space = False
        progressed = True
        while progressed:
            progressed = False
            dm = _DOTS.match(line, k)
            if dm:
                sep_has_dots = True
                k = dm.end()
                progressed = True
                continue
            sm = _SPACES.match(line, k)
            if sm:
                sep_has_space = True
                k = sm.end()
                progressed = True
        m2 = tail.match(line, k)
        if m2:
            if sep_has_space:
                glued = False
            if sep_has_dots:
                saw_dots = True
            refs += 1
            j = m2.end()
        else:
            break
    if refs >= 2 and (glued or saw_dots):
        return letter, j
    return None


# Underscore-less character grids such as "A1,1A1,2...A1,10" or
# "Y(1,1)Y(2,1)...Y(w,1)": a single letter followed by a multi-coordinate index
# written with a comma or with parentheses (instead of "_{...}").
_BARE2D_HEAD = re.compile(
    r'([A-Za-z])(\([^()]*\)|(?:[0-9]+|[A-Za-z])(?:,(?:[0-9]+|[A-Za-z]))+)')
_BARE2D_TAIL_BODY = \
    r'(?:\([^()]*\)|(?:[0-9]+|[A-Za-z])(?:,(?:[0-9]+|[A-Za-z]))+)'


def _try_bare_2d_run(line: str, start: int):
    m = _BARE2D_HEAD.match(line, start)
    if not m:
        return None
    letter = m.group(1)
    first_index = m.group(2)
    j = m.end()
    refs = 1
    glued = True
    saw_dots = False
    tail = re.compile(re.escape(letter) + _BARE2D_TAIL_BODY)
    while True:
        k = j
        sep_has_dots = False
        sep_has_space = False
        progressed = True
        while progressed:
            progressed = False
            dm = _DOTS.match(line, k)
            if dm:
                sep_has_dots = True
                k = dm.end()
                progressed = True
                continue
            sm = _SPACES.match(line, k)
            if sm:
                sep_has_space = True
                k = sm.end()
                progressed = True
        m2 = tail.match(line, k)
        if m2:
            if sep_has_space:
                glued = False
            if sep_has_dots:
                saw_dots = True
            refs += 1
            j = m2.end()
        else:
            break
    if refs >= 2 and (glued or saw_dots):
        return _strip_last_coord(letter, '_' + first_index), j
    return None


def _collapse_line(line: str) -> str:
    out = []
    i = 0
    n = len(line)
    while i < n:
        collapsed = (_try_collapse_run(line, i)
                     or _try_bare_2d_run(line, i)
                     or _try_bare_run(line, i))
        if collapsed:
            out.append(collapsed[0])
            i = collapsed[1]
        else:
            out.append(line[i])
            i += 1
    return ''.join(out)


_ABSTRACT_REF = re.compile(r'[A-Za-z]+_(?:\{([a-z])\}|([a-z]))$')


def _is_abstract_row(line: str) -> bool:
    """A purely illustrative row such as ``S_{i}`` or ``x_{i} y_{i}`` whose
    indices are all a single lowercase letter (the generic loop variable).
    These ``...`` / ``i``-th rows describe the shape but carry no extra data."""
    tokens = line.split()
    if not tokens:
        return False
    return all(_ABSTRACT_REF.fullmatch(tok) for tok in tokens)


def collapse_string_runs(input_format: str) -> str:
    """Return a variant of the format text where glued / dotted runs of a
    single variable are collapsed into a string (the fastest-varying index
    dimension is removed) and purely illustrative generic rows are dropped."""
    input_format = _normalize_separators(input_format)
    lines = [_collapse_line(line) for line in input_format.split('\n')]
    lines = [line for line in lines if not _is_abstract_row(line)]
    return '\n'.join(lines)


def _is_ascii(s):
    return all(ord(c) < 128 for c in s)


DOTS_PATTERNS = ["ldots", "cdots", "vdots", "ddots", "dots"]


def _is_noise(s):
    if any(pattern in s for pattern in DOTS_PATTERNS):
        return True

    return s == ":" or s == "...." or s == "..." or s == ".." or s == "."


def _normalize_index(text):
    return text.replace("{(", "").replace(")}", "")


def _divide_consecutive_vars(text):
    res_text = ""
    i = 0
    while i < len(text):
        if text[i] == "_":
            res_text += "_"
            i += 1

            if i < len(text) and text[i].isdigit():
                while i < len(text) and text[i].isdigit():
                    res_text += text[i]
                    i += 1
            elif i < len(text) and text[i].isalpha():
                res_text += text[i]
                i += 1
            if i < len(text) and text[i].isalpha():
                res_text += " "
        else:
            res_text += text[i]
            i += 1
    return res_text


def _remove_spaces_in_curly_brackets(input_format):
    res = []
    nest = 0
    for c in input_format:
        if c == '{':
            nest += 1
        elif c == '}':
            nest -= 1

        if c == ' ' and nest > 0:
            continue

        res.append(c)

    return "".join(res)


def _sanitized_tokens(input_format: str) -> List[str]:
    input_format = _normalize_separators(input_format)
    input_format = input_format.replace("\n", " ").replace("…", " ").replace("...", " ").replace(
        "..", " ").replace("\\ ", " ").replace("}", "} ").replace("　", " ").replace(", ", ",")
    input_format = _remove_spaces_in_curly_brackets(input_format)
    input_format = _divide_consecutive_vars(input_format)
    input_format = _normalize_index(input_format)
    input_format = input_format.replace("{", "").replace("}", "")

    tokens = [
        x for x in input_format.split(
        ) if x != "" and _is_ascii(
            x) and not _is_noise(
            x)]
    return tokens


class FormatSearcher:

    def __init__(self, tokens):
        self._token_manager = TokenManager(tokens)
        self._answers = None
        self._max_variables_count = None

    def search(self, max_variables_count) -> List[TokenizedFormat]:
        self._max_variables_count = max_variables_count
        self._answers = []
        self._inner_search([], {})
        return self._answers

    def _inner_search(self, var_token_seq, var_to_dim_num: Dict[str, int]):
        if len(var_to_dim_num) > self._max_variables_count:
            return

        if self._token_manager.is_terminal():
            self._answers.append(TokenizedFormat(copy.deepcopy(var_token_seq)))
            return

        for var_token in self._possible_var_tokens(self._token_manager.peek(), var_to_dim_num):
            next_var_to_dim_num = copy.deepcopy(var_to_dim_num)
            next_var_to_dim_num[var_token.var_name] = var_token.dim_num()
            try:
                var_token_seq.append(var_token)
                self._token_manager.go_next()
                self._inner_search(var_token_seq, next_var_to_dim_num)
            finally:
                self._token_manager.go_back()
                var_token_seq.pop()

    @staticmethod
    def _possible_var_tokens(token: str, current_var_to_dim_num: Dict[str, int]) -> List[VariableToken]:
        """
        Only considers to divide the given token into at most 3 pieces (that is, to assume at most 2 dimensional indexes).
        :param token: e.g. "N", "abc_1_2" or "a_1 ... a_N"
        :param current_var_to_dim_num: utilized to detect unknown variables (for pruning purpose)
        """
        var_token_candidates = [VariableToken(token, None, None)]
        var_token_candidates += [VariableToken(
            token[:i],
            token[i:],
            None) for i in range(1, len(token))]
        for i in range(1, len(token)):
            for j in range(i + 1, len(token)):
                var_token_candidates += [
                    VariableToken(token[:i], token[i:j], token[j:])]

        def check_if_possible(var_token: VariableToken):
            # check syntax error
            if not var_token.is_valid():
                return False

            # check kind of synonym error using current_var_to_dim_num
            for index in [var_token.first_index, var_token.second_index]:
                if index is None:
                    continue

                try:
                    for sub_var in CalcNode.parse(index).get_all_variables():
                        if sub_var not in current_var_to_dim_num:
                            return False
                except CalcParseError:
                    return False

            if var_token.var_name in current_var_to_dim_num \
                    and current_var_to_dim_num[var_token.var_name] != var_token.dim_num():
                return False
            return True

        return [var_token for var_token in var_token_candidates if check_if_possible(var_token)]


def search_formats_with_minimum_vars(input_format: str) -> List[TokenizedFormat]:
    """
    Fast enough for realistic instances.
    This method returns possible formats with the smallest number of variables.
    """
    tokens = _sanitized_tokens(input_format)
    searcher = FormatSearcher(tokens)
    for max_variable_length in range(1, 20):
        result = searcher.search(max_variable_length)
        if result:
            return result
    raise NoFormatFoundError


class NoFormatFoundError(Exception):
    pass
