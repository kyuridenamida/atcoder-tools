from typing import List, Tuple, Optional

from bs4 import BeautifulSoup

from atcodertools.client.models.sample import Sample
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


class SampleDetectionError(Exception):
    pass


class InputFormatDetectionError(Exception):
    pass


class ProblemContent:

    def __init__(self, input_format_text: Optional[str] = None,
                 samples: Optional[List[Sample]] = None,
                 original_html: Optional[str] = None,
                 ):
        self.samples = samples
        self.input_format_text = input_format_text
        self.original_html = original_html

    @classmethod
    def from_html(cls, html: str):
        res = ProblemContent(original_html=html)
        soup = BeautifulSoup(html, "html.parser")
        res.input_format_text, res.samples = res._extract_input_format_and_samples(
            soup)
        return res

    def get_input_format(self) -> str:
        return self.input_format_text

    def get_samples(self) -> List[Sample]:
        return self.samples

    @staticmethod
    def _extract_input_format_and_samples(soup) -> Tuple[str, List[Sample]]:

        # Remove English statements
        for e in soup.findAll("span", {"class": "lang-en"}):
            e.extract()

        # Focus on AtCoder's usual contest's html structure
        tmp = soup.select('.part')
        if tmp:
            tmp[0].extract()

        try:
            try:
                input_format_tag, input_tags, output_tags = ProblemContent._primary_strategy(
                    soup)
                if input_format_tag is None:
                    raise InputFormatDetectionError
            except InputFormatDetectionError:
                input_format_tag, input_tags, output_tags = ProblemContent._secondary_strategy(
                    soup)
        except Exception as e:
            raise InputFormatDetectionError(e)

        if len(input_tags) != len(output_tags):
            raise SampleDetectionError

        try:
            res = [Sample(normalize(in_tag.text), normalize(out_tag.text))
                   for in_tag, out_tag in zip(input_tags, output_tags)]

            if input_format_tag is None:
                raise InputFormatDetectionError

            input_format_text = normalize(input_format_tag.text)
        except AttributeError:
            raise InputFormatDetectionError

        return input_format_text, res

    @staticmethod
    def _primary_strategy(soup):
        input_tags = []
        output_tags = []
        input_format_tag = None
        for tag in soup.select('section'):
            h3tag = tag.find('h3')
            if h3tag is None:
                continue
            # Some problems have strange characters in h3 tags which should be
            # removed
            section_title = remove_non_jp_characters(tag.find('h3').get_text())

            if section_title.startswith("入力例"):
                input_tags.append(tag.find('pre'))
            elif section_title.startswith("入力"):
                input_format_tag = tag.find('pre')

            if section_title.startswith("出力例"):
                output_tags.append(tag.find('pre'))
        return input_format_tag, input_tags, output_tags

    @staticmethod
    def _secondary_strategy(soup):  # TODO: more descriptive name
        pre_tags = soup.select('pre')
        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tag = pre_tags[0]
        return input_format_tag, input_tags, output_tags
