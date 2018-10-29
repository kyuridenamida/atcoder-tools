from typing import List, Tuple

from bs4 import BeautifulSoup

from core.models.Sample import Sample
from core.utils import normalized, remove_non_jp_characters


class SampleParseError(Exception):
    pass


class InputParseError(Exception):
    pass


class ProblemContent:
    input_format_text = None
    samples = None

    def get_input_format(self) -> str:
        return self.input_format_text

    def get_samples(self) -> List[Sample]:
        return self.samples

    def __init__(self, req):
        self.soup = BeautifulSoup(req, "html.parser")
        self.remove_english_statements()
        self.focus_on_atcoder_format()
        self.input_format_text, self.samples = self.extract_input_format_and_samples()

    def remove_english_statements(self):
        for e in self.soup.findAll("span", {"class": "lang-en"}):
            e.extract()

    def focus_on_atcoder_format(self):
        # Preferably use atCoder format
        tmp = self.soup.select('.part')
        if tmp:
            tmp[0].extract()

    def extract_input_format_and_samples(self) -> Tuple[str, List[Sample]]:
        try:
            input_format_tag, input_tags, output_tags = self.prior_strategy()
            if input_format_tag is None:
                raise InputParseError
        except InputParseError:
            input_format_tag, input_tags, output_tags = self.alternative_strategy()

        if len(input_tags) != len(output_tags):
            raise SampleParseError

        res = [Sample(normalized(in_tag.text), normalized(out_tag.text))
               for in_tag, out_tag in zip(input_tags, output_tags)]

        if input_format_tag is None:
            raise InputParseError

        input_format_text = normalized(input_format_tag.text)

        return input_format_text, res

    def prior_strategy(self):  # TODO: more descriptive name
        input_tags = []
        output_tags = []
        input_format_tag = None
        for tag in self.soup.select('section'):
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

    def alternative_strategy(self):  # TODO: more descriptive name
        pre_tags = self.soup.select('pre')
        sample_tags = pre_tags[1:]
        input_tags = sample_tags[0::2]
        output_tags = sample_tags[1::2]
        input_format_tag = pre_tags[0]
        return input_format_tag, input_tags, output_tags
