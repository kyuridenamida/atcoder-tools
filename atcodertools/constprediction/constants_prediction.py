import re
from typing import Tuple, Optional

from atcodertools.models.constpred.problem_constant_set import ProblemConstantSet
from bs4 import BeautifulSoup

from atcodertools.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError


def split_into_sentences(text: str):
    return text.split("\n")


def is_interesting_sentence(sentence, keywords):
    for kw in keywords:
        if kw in sentence:
            return True
    return False


PRIMARY_STRATEGY_RE = re.compile("([0-9]+).?.?.?で割った")
SECONDARY_STRATEGY_RE = re.compile("modu?l?o?[^0-9]?[^0-9]?[^0-9]?([0-9]+)")


def predict_modulo(html: str):
    def normalize(sentence):
        return sentence.replace('\\', '').replace("{", "").replace("}", "").replace(",", "").replace(" ", "").replace(
            "10^9+7", "1000000007").lower().strip()

    mod_anchors = ["余り", "あまり", "mod", "割っ", "modulo"]

    soup = BeautifulSoup(html, "html.parser")
    sentences = split_into_sentences(soup.get_text())
    sentences = [
        normalize(s) for s in sentences if is_interesting_sentence(s, mod_anchors)]

    res = None

    for s in sentences:
        for regexp in [PRIMARY_STRATEGY_RE, SECONDARY_STRATEGY_RE]:
            m = regexp.search(s)
            if m is not None:
                extracted_val = int(m.group(1))
                if res is None or res < extracted_val:
                    res = extracted_val
    return res


# yes_str, no_str
def predict_yes_no(html: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        outputs = set()
        for sample in ProblemContent.from_html(html).get_samples():
            for x in sample.get_output().split():
                outputs.add(x)
    except (InputFormatDetectionError, SampleDetectionError):
        return None, None

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
    yes_str, no_str = predict_yes_no(html)
    mod = predict_modulo(html)
    return ProblemConstantSet(mod=mod, yes_str=yes_str, no_str=no_str)
