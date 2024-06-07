import re
from typing import Tuple, Optional

from bs4 import BeautifulSoup

from atcodertools.client.models.problem_content import ProblemContent, InputFormatDetectionError, SampleDetectionError
from atcodertools.common.judgetype import ErrorType, NormalJudge, DecimalJudge, Judge
from atcodertools.common.logging import logger
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
import math


class YesNoPredictionFailedError(Exception):
    pass


class MultipleModCandidatesError(Exception):

    def __init__(self, cands):
        self.cands = cands


class MultipleLimitCandidatesError(Exception):

    def __init__(self, cands):
        self.cands = cands


class NoDecimalCandidatesError(Exception):
    pass


class MultipleDecimalCandidatesError(Exception):

    def __init__(self, cands):
        self.cands = cands


class FailingToKnowFormatAnalysisAllowedByRuleError(Exception):
    def __init__(self, reason):
        self.reason = reason


MOD_ANCHORS = ["余り", "あまり", "mod", "割っ", "modulo"]
DECIMAL_ANCHORS = ["誤差", " error "]
LIMIT_ANCHORS = ["時間制限", "Time Limit"]

MOD_STRATEGY_RE_LIST = [
    re.compile("([0-9]+).?.?.?で割った"),
    re.compile("modu?l?o?[^0-9]?[^0-9]?[^0-9]?([0-9]+)")
]

DECIMAL_STRATEGY_RE_LIST_KEYWORD = [
    re.compile("(?:絶対|相対)誤差"),
    re.compile("(?:absolute|relative)")
]

DECIMAL_STRATEGY_RE_LIST_VAL = [
    re.compile("10\^(-[0-9]+)"),
    re.compile("1e(-[0-9]+)")
]

LIMIT_STRATEGY_RE_LIST = [
    re.compile("([0-9.]+)\s*sec")
]


def is_mod_context(sentence):
    for kw in MOD_ANCHORS:
        if kw in sentence:
            return True
    return False


def is_decimal_context(sentence):
    for kw in DECIMAL_ANCHORS:
        if kw in sentence:
            return True
    return False


def is_limit_context(sentence):
    for kw in LIMIT_ANCHORS:
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


def predict_judge_method(html: str) -> Judge:
    def normalize(sentence):
        return sentence.replace('\\', '').replace("{", "").replace("}", "").replace(",", "").replace(" ", "").replace(
            "−", "-").lower().strip()

    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.get_text().split("\n")
    sentences = [normalize(s) for s in sentences if is_decimal_context(s)]

    decimal_keyword_cands = set()
    decimal_val_cands = set()

    if len(sentences) > 0:  # Decimal
        is_absolute = False
        is_relative = False
        for s in sentences:
            for regexp in DECIMAL_STRATEGY_RE_LIST_KEYWORD:
                r = regexp.findall(s)
                for t in r:
                    if t == "絶対誤差" or t == "absolute":
                        is_absolute = True
                    elif t == "相対誤差" or t == "relative":
                        is_relative = True
                    decimal_keyword_cands.add(t)
        for s in sentences:
            for regexp in DECIMAL_STRATEGY_RE_LIST_VAL:
                r = regexp.findall(s)
                for t in r:
                    decimal_val_cands.add(int(t))

        if len(decimal_val_cands) == 0:
            raise NoDecimalCandidatesError

        if len(decimal_val_cands) == 1:
            if is_absolute and is_relative:
                error_type = ErrorType.AbsoluteOrRelative
            elif is_absolute:
                error_type = ErrorType.Absolute
            else:
                assert is_relative
                error_type = ErrorType.Relative

            return DecimalJudge(error_type, 10.0**(int(list(decimal_val_cands)[0])))

        raise MultipleDecimalCandidatesError(decimal_val_cands)

    return NormalJudge()


def predict_limit(html: str) -> Optional[int]:
    def normalize(sentence):
        return sentence.replace('\\', '').replace("{", "").replace("}", "").replace(",", "").replace(" ", "").lower().strip()

    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.get_text().split("\n")
    sentences = [normalize(s) for s in sentences if is_limit_context(s)]

    limit_cands = set()

    for s in sentences:
        for regexp in LIMIT_STRATEGY_RE_LIST:
            m = regexp.search(s)
            if m is not None:
                extracted_val = float(m.group(1))
                limit_cands.add(extracted_val)

    if len(limit_cands) == 0:
        return None

    if len(limit_cands) == 1:
        return math.floor(list(limit_cands)[0] * 1000.0 + 0.5)

    raise MultipleModCandidatesError(limit_cands)


def predict_is_format_analysis_allowed_by_rule(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    url_meta_tag = soup.find("meta", property="og:url")
    if url_meta_tag is None:
        raise FailingToKnowFormatAnalysisAllowedByRuleError(
            "No meta tag detected, which is important as a clue to know if the input analysis is allowed.")

    # ABC is the target of "No LLM rules" by AtCoder (See https://info.atcoder.jp/entry/llm-abc-rules-ja or https://info.atcoder.jp/entry/llm-abc-rules-en)
    is_target_contest_of_no_llm_rule = "/contests/abc" in url_meta_tag["content"]

    # If there is no virtual standings link, assume it's ongoing.
    is_ongoing_contest = len([tag for tag in soup.find_all(
        "a") if "/standings/virtual" in tag.get("href", "")]) == 0

    if is_target_contest_of_no_llm_rule and is_ongoing_contest:
        return False

    return True


def predict_constants(html: str) -> ProblemConstantSet:
    try:
        yes_str, no_str = predict_yes_no(html)
    except YesNoPredictionFailedError:
        yes_str = no_str = None

    try:
        mod = predict_modulo(html)
    except MultipleModCandidatesError as e:
        logger.warning("Modulo prediction failed -- "
                       "two or more candidates {} are detected as modulo values".format(e.cands))
        mod = None

    try:
        judge = predict_judge_method(html)
    except MultipleModCandidatesError as e:
        logger.warning("decimal prediction failed -- "
                       "two or more candidates {} are detected as decimal values".format(e.cands))
        judge = NormalJudge()

    try:
        timeout = predict_limit(html)
    except MultipleLimitCandidatesError as e:
        logger.warning("limit prediction failed -- "
                       "two or more candidates {} are detected as limit".format(e.cands))
        timeout = None

    try:
        is_format_analysis_allowed_by_rule = predict_is_format_analysis_allowed_by_rule(
            html)
    except FailingToKnowFormatAnalysisAllowedByRuleError as e:
        logger.warning(
            "Failed to know whether format analysis is allowed by the contest rules -- ", e.reason)
        is_format_analysis_allowed_by_rule = None

    return ProblemConstantSet(
        mod=mod,
        yes_str=yes_str,
        no_str=no_str,
        judge_method=judge,
        timeout=timeout,
        is_format_analysis_allowed_by_rule=is_format_analysis_allowed_by_rule,
    )
