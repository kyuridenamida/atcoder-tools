import logging
import re
from typing import Tuple, Optional

from bs4 import BeautifulSoup

from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.client.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError


class YesNoPredictionFailedError(Exception):
    pass


class MultipleModCandidatesError(Exception):

    def __init__(self, cands):
        self.cands = cands


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


def predict_modulo(html: str) -> Optional[int]:
    def normalize(sentence):
        return sentence.replace('\\', '').replace("{", "").replace("}", "").replace(",", "").replace(" ", "").replace(
            "10^9+7", "1000000007").lower().strip()

    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.get_text().split("\n")
    sentences = [normalize(s) for s in sentences if is_mod_context(s)]

    mod_cands = set()

    for s in sentences:
        for regexp in MOD_STRATEGY_RE_LIST:
            m = regexp.search(s)
            if m is not None:
                extracted_val = int(m.group(1))
                mod_cands.add(extracted_val)

    if len(mod_cands) == 0:
        return None

    if len(mod_cands) == 1:
        return list(mod_cands)[0]

    raise MultipleModCandidatesError(mod_cands)


def predict_yes_no(html: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        outputs = set()
        for sample in ProblemContent.from_html(html).get_samples():
            for x in sample.get_output().split("\n"):
                outputs.add(x.strip())
    except (InputFormatDetectionError, SampleDetectionError) as e:
        raise YesNoPredictionFailedError(e)

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
    try:
        yes_str, no_str = predict_yes_no(html)
    except YesNoPredictionFailedError:
        yes_str = no_str = None

    try:
        mod = predict_modulo(html)
    except MultipleModCandidatesError as e:
        logging.warning("Modulo prediction failed -- "
                        "two or more candidates {} are detected as modulo values".format(e.cands))
        mod = None

    return ProblemConstantSet(mod=mod, yes_str=yes_str, no_str=no_str)
