import re
import unicodedata


def is_japanese(ch):
    # Thank you!
    # http://minus9d.hatenablog.com/entry/2015/07/16/231608
    try:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return True
    except ValueError:
        pass
    return False


def remove_non_jp_characters(content):
    return "".join([x for x in content if is_japanese(x)])


def normalized(content: str) -> str:
    return content.strip().replace('\r', '') + "\n"


def fixed_variable_name(name):
    if name[-1] == "_":
        return name[:-1]
    return name


def is_arithmetic_sequence(seq):
    if len(seq) <= 1:
        return True
    for i in range(1, len(seq)):
        if seq[1] - seq[0] != seq[i] - seq[i - 1]:
            return False
    return True
