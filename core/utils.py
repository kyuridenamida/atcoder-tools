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


def pure_japanese_text(content):
    return "".join([x for x in content if is_japanese(x)])


def normalized(content):
    return content.strip().replace('\r', '') + "\n"


def fixed_variable_name(name):
    if name[-1] == "_":
        return name[:-1]
    return name


def is_float(text):
    return re.match("-?\d+\.\d+$", text) is not None


def is_int(text):
    return re.match("-?\d+$", text) is not None


def is_arithmetic_sequence(seq):
    if len(seq) <= 1:
        return True
    for i in range(1, len(seq)):
        if seq[1] - seq[0] != seq[i] - seq[i - 1]:
            return False
    return True


def normalize_index(text):
    return text.replace("{(", "").replace(")}", "")


def divide_consecutive_vars(text):
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


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def is_noise(s):
    return s == ":" or s == "...." or s == "..." or s == ".." or s == "."


if __name__ == "__main__":
    print(divide_consecutive_vars("hello_1234world1"))
    print(normalize_index("A_{(H,W)}"))
