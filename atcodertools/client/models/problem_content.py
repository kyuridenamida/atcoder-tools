from typing import List, Optional

from bs4 import BeautifulSoup
from onlinejudge.service.atcoder import AtCoderProblem, AtCoderProblemContent

from atcodertools.client.models.sample import Sample


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

    def get_input_format(self) -> str:
        if self.input_format_text is None:
            raise SampleDetectionError
        return self.input_format_text

    def get_samples(self) -> List[Sample]:
        if self.samples is None:
            raise SampleDetectionError
        return self.samples

    def get_original_html(self) -> str:
        assert self.original_html is not None
        return self.original_html

    @classmethod
    def from_raw_content(cls, content: AtCoderProblemContent) -> 'ProblemContent':
        if not content.input_format:
            raise InputFormatDetectionError
        input_format_text = BeautifulSoup(content.input_format, 'lxml').text

        if not content.sample_cases:
            raise SampleDetectionError
        samples = []
        for testcase in content.sample_cases:
            if testcase.output_data is not None:
                samples += [Sample(testcase.input_data.decode(),
                                   testcase.output_data.decode())]

        return ProblemContent(input_format_text=input_format_text, samples=samples, original_html=content.html)

    @classmethod
    def from_html(cls, html: str) -> 'ProblemContent':
        problem = AtCoderProblem.from_url(
            'https://practice.contest.atcoder.jp/tasks/practice_1')  # dummy
        return cls.from_raw_content(AtCoderProblemContent.from_html(html, problem))
