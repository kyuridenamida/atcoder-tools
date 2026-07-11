from typing import List, Tuple, Optional

from bs4 import BeautifulSoup

from atcodertools.client.models.sample import Sample

import unicodedata


def remove_non_jp_characters(content):
    return "".join([x for x in content if is_japanese(x)])


def normalize(content: str) -> str:
    return content.strip().replace('\r', '') + "\n"


def normalize_context(content: str) -> str:
    return " ".join(content.replace('\r', '').split())


def is_japanese(ch):
    # Thank you!
    # http://minus9d.hatenablog.com/entry/2015/07/16/231608
    try:
        name = unicodedata.name(ch)
        if (
            "CJK UNIFIED" in name
            or "HIRAGANA" in name
            or "KATAKANA" in name
        ):
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
        samples: Optional[List[Sample]] = None,
        original_html: Optional[str] = None,
        input_format_blocks: Optional[List[str]] = None,
        input_format_context_text: Optional[str] = None,
    ):
        self.samples = samples
        self.input_format_text = input_format_text
        self.original_html = original_html

        if input_format_blocks is None:
            if input_format_text is None:
                input_format_blocks = []
            else:
                input_format_blocks = [input_format_text]

        self.input_format_blocks = list(input_format_blocks)
        self.input_format_context_text = (
            input_format_context_text
            if input_format_context_text is not None
            else ""
        )

    @classmethod
    def from_html(cls, html: str):
        res = ProblemContent(original_html=html)
        soup = BeautifulSoup(html, "html.parser")

        (
            res.input_format_text,
            res.input_format_blocks,
            res.input_format_context_text,
            res.samples,
        ) = res._extract_input_format_and_samples(soup)

        return res

    def get_input_format(self) -> str:
        """
        Return the first input-format block for backward compatibility.
        """
        return self.input_format_text

    def get_input_format_blocks(self) -> List[str]:
        return list(self.input_format_blocks)

    def get_input_format_context(self) -> str:
        return self.input_format_context_text

    def get_samples(self) -> List[Sample]:
        return self.samples

    @staticmethod
    def _extract_input_format_and_samples(
        soup,
    ) -> Tuple[str, List[str], str, List[Sample]]:
        # Remove English statements.
        for element in soup.find_all(
            "span",
            {"class": "lang-en"},
        ):
            element.extract()

        # Focus on AtCoder's usual contest HTML structure.
        parts = soup.select('.part')
        if parts:
            parts[0].extract()

        try:
            try:
                (
                    input_format_tags,
                    input_format_context,
                    input_tags,
                    output_tags,
                ) = ProblemContent._primary_strategy(soup)

                if not input_format_tags:
                    raise InputFormatDetectionError
            except InputFormatDetectionError:
                (
                    input_format_tags,
                    input_format_context,
                    input_tags,
                    output_tags,
                ) = ProblemContent._secondary_strategy(soup)
        except Exception as error:
            raise InputFormatDetectionError(error)

        if len(input_tags) != len(output_tags):
            raise SampleDetectionError

        try:
            samples = [
                Sample(
                    normalize(input_tag.text),
                    normalize(output_tag.text),
                )
                for input_tag, output_tag
                in zip(input_tags, output_tags)
            ]

            if not input_format_tags:
                raise InputFormatDetectionError

            input_format_blocks = [
                normalize(input_format_tag.text)
                for input_format_tag in input_format_tags
            ]
        except AttributeError:
            raise InputFormatDetectionError

        return (
            input_format_blocks[0],
            input_format_blocks,
            normalize_context(input_format_context),
            samples,
        )

    @staticmethod
    def _primary_strategy(soup):
        input_tags = []
        output_tags = []
        input_format_tags = None
        input_format_context = ""

        for tag in soup.select('section'):
            h3tag = tag.find('h3')
            if h3tag is None:
                continue

            # Some problems have strange characters in h3 tags which should
            # be removed.
            section_title = remove_non_jp_characters(
                h3tag.get_text()
            )

            if section_title.startswith("入力例"):
                input_tags.append(tag.find('pre'))
            elif section_title.startswith("入力"):
                input_format_tags = tag.find_all('pre')
                input_format_context = tag.get_text(
                    " ",
                    strip=True,
                )

            if section_title.startswith("出力例"):
                output_tags.append(tag.find('pre'))

        return (
            input_format_tags,
            input_format_context,
            input_tags,
            output_tags,
        )

    @staticmethod
    def _secondary_strategy(soup):
        # TODO: more descriptive name
        pre_tags = soup.select('pre')

        if not pre_tags:
            raise InputFormatDetectionError

        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tags = [pre_tags[0]]

        return (
            input_format_tags,
            "",
            input_tags,
            output_tags,
        )
