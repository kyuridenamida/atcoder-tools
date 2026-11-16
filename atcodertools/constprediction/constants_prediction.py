import re
from typing import Optional

from bs4 import BeautifulSoup

from atcodertools.client.models.problem_content import InputFormatDetectionError, ProblemContent, SampleDetectionError
from atcodertools.common.judgetype import DecimalJudge, ErrorType, InteractiveJudge, Judge, NormalJudge
from atcodertools.common.logging import logger
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet


class YesNoPredictionFailedError(Exception):
    pass


class MultipleModCandidatesError(Exception):
    def __init__(self, cands: set[int]) -> None:
        self.cands = cands


class MultipleDecimalCandidatesError(Exception):
    def __init__(self, cands: set[int]) -> None:
        self.cands = cands


MOD_ANCHORS = ["余り", "あまり", "mod", "割っ", "modulo"]
DECIMAL_ANCHORS = ["誤差", " error "]
MULTISOLUTION_ANCHORS = ["複数ある場合", "どれを出力しても構わない"]
INTERACTIVE_ANCHORS = ["インタラクティブ", "リアクティブ", "interactive", "reactive"]

MOD_STRATEGY_RE_LIST = [re.compile("([0-9]+).?.?.?で割った"), re.compile("modu?l?o?[^0-9]?[^0-9]?[^0-9]?([0-9]+)")]

DECIMAL_STRATEGY_RE_LIST_KEYWORD = [re.compile("(?:絶対|相対)誤差"), re.compile("(?:absolute|relative)")]
DECIMAL_STRATEGY_RE_LIST_VAL = [
    re.compile("10\^(-[0-9]+)"),
]


def is_mod_context(sentence: str) -> bool:
    return any(kw in sentence for kw in MOD_ANCHORS)


def is_decimal_context(sentence: str) -> bool:
    return any(kw in sentence for kw in DECIMAL_ANCHORS)


def predict_modulo(html: str) -> Optional[int]:
    def normalize(sentence: str) -> str:
        return (
            sentence.replace("\\", "")
            .replace("{", "")
            .replace("}", "")
            .replace(",", "")
            .replace(" ", "")
            .replace("10^9+7", "1000000007")
            .lower()
            .strip()
        )

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


def predict_yes_no(html: str) -> tuple[Optional[str], Optional[str]]:
    try:
        outputs = set()
        samples = ProblemContent.from_html(html).get_samples()
        assert samples is not None
        for sample in samples:
            for x in sample.get_output().split("\n"):
                outputs.add(x.strip())
    except (InputFormatDetectionError, SampleDetectionError) as e:
        raise YesNoPredictionFailedError(e) from e

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


def predict_judge_method(html: str) -> Judge:
    def normalize(sentence: str) -> str:
        return (
            sentence.replace("\\", "")
            .replace("{", "")
            .replace("}", "")
            .replace(",", "")
            .replace(" ", "")
            .replace("−", "-")
            .lower()
            .strip()
        )

    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.get_text().split("\n")

    interactive_sentences = []

    for s in sentences:
        for kw in INTERACTIVE_ANCHORS:
            if kw in s:
                interactive_sentences.append(s)

    if len(interactive_sentences) > 0:
        return InteractiveJudge()

    decimal_sentences = [normalize(s) for s in sentences if is_decimal_context(s)]

    decimal_keyword_cands = set()
    decimal_val_cands = set()

    if len(decimal_sentences) > 0:  # Decimal
        is_absolute = False
        is_relative = False
        for s in decimal_sentences:
            for regexp in DECIMAL_STRATEGY_RE_LIST_KEYWORD:
                r = regexp.findall(s)
                for t in r:
                    if t == "絶対誤差" or t == "absolute":
                        is_absolute = True
                    elif t == "相対誤差" or t == "relative":
                        is_relative = True
                    decimal_keyword_cands.add(t)
        for s in decimal_sentences:
            for regexp in DECIMAL_STRATEGY_RE_LIST_VAL:
                r = regexp.findall(s)
                for t in r:
                    decimal_val_cands.add(int(t))

        if len(decimal_val_cands) == 0:
            # No error value candidate is found
            return NormalJudge()

        if len(decimal_val_cands) == 1:
            if is_absolute and is_relative:
                error_type = ErrorType.AbsoluteOrRelative
            elif is_absolute:
                error_type = ErrorType.Absolute
            else:
                assert is_relative
                error_type = ErrorType.Relative

            return DecimalJudge(error_type, 10.0 ** (int(list(decimal_val_cands)[0])))

        raise MultipleDecimalCandidatesError(decimal_val_cands)

    return NormalJudge()


def predict_constants(html: str) -> ProblemConstantSet:
    try:
        yes_str, no_str = predict_yes_no(html)
    except YesNoPredictionFailedError:
        yes_str = no_str = None

    try:
        mod = predict_modulo(html)
    except MultipleModCandidatesError as e:
        logger.warning(f"Modulo prediction failed -- two or more candidates {e.cands} are detected as modulo values")
        mod = None

    try:
        judge = predict_judge_method(html)
    except MultipleDecimalCandidatesError as e:
        logger.warning(f"decimal prediction failed -- two or more candidates {e.cands} are detected as decimal values")
        judge = NormalJudge()

    return ProblemConstantSet(mod=mod, yes_str=yes_str, no_str=no_str, judge_method=judge)
