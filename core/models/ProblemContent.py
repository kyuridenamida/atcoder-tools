from typing import List, Tuple

from bs4 import BeautifulSoup

from core.models.Sample import Sample
import unicodedata


def remove_non_jp_characters(content):
    return "".join([x for x in content if is_japanese(x)])


def normalize(content: str) -> str:
    return content.strip().replace('\r', '') + "\n"


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


class SampleParseError(Exception):
    pass


class InputParseError(Exception):
    pass


class ProblemContent:
    def __init__(self, req=None):
        if req:
            self._soup = BeautifulSoup(req, "html.parser")
            self._remove_english_statements()
            self._focus_on_atcoder_format()
            self.input_format_text, self.samples = self._extract_input_format_and_samples()
        else:
            self.input_format_text, self.samples = None, None

    @staticmethod
    def of(input_format_text: str, samples: List[Sample]):
        res = ProblemContent()
        res.samples = samples
        res.input_format_text = input_format_text
        return res

    def get_input_format(self) -> str:
        return self.input_format_text

    def get_samples(self) -> List[Sample]:
        return self.samples

    def _remove_english_statements(self):
        for e in self._soup.findAll("span", {"class": "lang-en"}):
            e.extract()

    def _focus_on_atcoder_format(self):
        # Preferably use atCoder format
        tmp = self._soup.select('.part')
        if tmp:
            tmp[0].extract()

    def _extract_input_format_and_samples(self) -> Tuple[str, List[Sample]]:
        try:
            try:
                input_format_tag, input_tags, output_tags = self._prior_strategy()
                if input_format_tag is None:
                    input_format_tag, input_tags, output_tags = self._alternative_strategy()
            except InputParseError:
                input_format_tag, input_tags, output_tags = self._alternative_strategy()
        except Exception as e:
            raise InputParseError(e)

        if len(input_tags) != len(output_tags):
            raise SampleParseError

        res = [Sample(normalize(in_tag.text), normalize(out_tag.text))
               for in_tag, out_tag in zip(input_tags, output_tags)]

        if input_format_tag is None:
            raise InputParseError

        input_format_text = normalize(input_format_tag.text)

        return input_format_text, res

    def _prior_strategy(self):  # TODO: more descriptive name
        input_tags = []
        output_tags = []
        input_format_tag = None
        for tag in self._soup.select('section'):
            h3tag = tag.find('h3')
            if h3tag is None:
                continue
            # Some problem has strange characters in h3 tags which should be removed
            section_title = remove_non_jp_characters(tag.find('h3').get_text())

            if section_title.startswith("入力例"):
                input_tags.append(tag.find('pre'))
            elif section_title.startswith("入力"):
                input_format_tag = tag.find('pre')

            if section_title.startswith("出力例"):
                output_tags.append(tag.find('pre'))
        return input_format_tag, input_tags, output_tags

    def _alternative_strategy(self):  # TODO: more descriptive name
        pre_tags = self._soup.select('pre')
        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tag = pre_tags[0]
        return input_format_tag, input_tags, output_tags
