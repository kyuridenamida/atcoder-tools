import re
from typing import Tuple, Optional

from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from bs4 import BeautifulSoup

from atcodertools.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError

MOD_ANCHORS = ["余り", "あまり", "mod", "割っ", "modulo"]

MOD_STRATEGY_RE_LIST = [
    re.compile("([0-9]+).?.?.?で割った"),
    re.compile("modu?l?o?[^0-9]?[^0-9]?[^0-9]?([0-9]+)")
]


def is_mod_context(sentence):
    for kw in MOD_ANCHORS:
        if kw in sentence:
            return True
    return False


def predict_modulo(html: str):
    def normalize(sentence):
        return sentence.replace('\\', '').replace("{", "").replace("}", "").replace(",", "").replace(" ", "").replace(
            "10^9+7", "1000000007").lower().strip()

    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.get_text().split("\n")
    sentences = [normalize(s) for s in sentences if is_mod_context(s)]

    res = None

    for s in sentences:
        for regexp in MOD_STRATEGY_RE_LIST:
            m = regexp.search(s)
            if m is not None:
                extracted_val = int(m.group(1))
                if res is None or res < extracted_val:
                    res = extracted_val
    return res


def predict_yes_no(html: str) -> Optional[Tuple[str, str]]:
    try:
        outputs = set()
        for sample in ProblemContent.from_html(html).get_samples():
            for x in sample.get_output().split():
                outputs.add(x)
    except (InputFormatDetectionError, SampleDetectionError):
        return None

    yes_kws = ["yes", "possible"]
    no_kws = ["no", "impossible"]

    yes_str = None
    no_str = None
    for val in outputs:
        if val.lower() in yes_kws:
            yes_str = val
        if val.lower() in no_kws:
            no_str = val

    return yes_str, no_str


def predict_constants(html: str) -> ProblemConstantSet:
    yes_no_result = predict_yes_no(html)
    if yes_no_result is None:
        yes_str = no_str = None
    else:
        yes_str, no_str = yes_no_result

    mod = predict_modulo(html)
    return ProblemConstantSet(mod=mod, yes_str=yes_str, no_str=no_str)
