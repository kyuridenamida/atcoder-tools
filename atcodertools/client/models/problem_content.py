import unicodedata
from typing import Any, Optional

from bs4 import BeautifulSoup

from atcodertools.client.models.sample import Sample


def remove_non_jp_characters(content: str) -> str:
    return "".join([x for x in content if is_japanese(x)])


def normalize(content: str) -> str:
    return content.strip().replace("\r", "") + "\n"


def is_japanese(ch: str) -> bool:
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
    def __init__(
        self,
        input_format_text: Optional[str] = None,
        samples: Optional[list[Sample]] = None,
        original_html: Optional[str] = None,
    ) -> None:
        self.samples = samples
        self.input_format_text = input_format_text
        self.original_html = original_html

    @classmethod
    def from_html(cls, html: str) -> "ProblemContent":
        res = ProblemContent(original_html=html)
        soup = BeautifulSoup(html, "html.parser")
        res.input_format_text, res.samples = res._extract_input_format_and_samples(soup)
        return res

    def get_input_format(self) -> Optional[str]:
        return self.input_format_text

    def get_samples(self) -> Optional[list[Sample]]:
        return self.samples

    @staticmethod
    def _extract_input_format_and_samples(soup: BeautifulSoup) -> tuple[str, list[Sample]]:

        # Remove English statements
        for e in soup.find_all("span", {"class": "lang-en"}):
            e.extract()

        # Focus on AtCoder's usual contest's html structure
        tmp = soup.select(".part")
        if tmp:
            tmp[0].extract()

        try:
            try:
                input_format_tag, input_tags, output_tags = ProblemContent._primary_strategy(soup)
                if input_format_tag is None:
                    raise InputFormatDetectionError
            except InputFormatDetectionError:
                input_format_tag, input_tags, output_tags = ProblemContent._secondary_strategy(soup)
        except Exception as e:
            raise InputFormatDetectionError(e) from e

        if len(input_tags) != len(output_tags):
            raise SampleDetectionError

        try:
            res = [
                Sample(normalize(in_tag.text), normalize(out_tag.text))
                for in_tag, out_tag in zip(input_tags, output_tags)
            ]

            if input_format_tag is None:
                raise InputFormatDetectionError

            input_format_text = normalize(input_format_tag.text)
        except AttributeError as e:
            raise InputFormatDetectionError from e

        return input_format_text, res

    @staticmethod
    def _primary_strategy(soup: BeautifulSoup) -> tuple[Any, list[Any], list[Any]]:
        input_tags = []
        output_tags = []
        input_format_tag = None
        for tag in soup.select("section"):
            h3tag = tag.find("h3")
            if h3tag is None:
                continue
            # Some problems have strange characters in h3 tags which should be
            # removed
            section_title = remove_non_jp_characters(h3tag.get_text())

            if section_title.startswith("入力例"):
                input_tags.append(tag.find("pre"))
            elif section_title.startswith("入力"):
                input_format_tag = tag.find("pre")

            if section_title.startswith("出力例"):
                output_tags.append(tag.find("pre"))
        return input_format_tag, input_tags, output_tags

    @staticmethod
    def _secondary_strategy(soup: BeautifulSoup) -> tuple[Any, list[Any], list[Any]]:  # TODO: more descriptive name
        pre_tags = soup.select("pre")
        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tag = pre_tags[0]
        return input_format_tag, input_tags, output_tags


def get_problem_content(original_html: str) -> ProblemContent:
    try:
        return ProblemContent.from_html(original_html)
    except (InputFormatDetectionError, SampleDetectionError) as e:
        raise e
