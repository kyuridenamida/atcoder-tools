import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from atcodertools.client.models.problem_content import (
    ProblemContent,
)


class InputTokenKind(Enum):
    WORD = "word"
    INTEGER = "integer"
    ELLIPSIS = "ellipsis"
    DELIMITER = "delimiter"
    SYMBOL = "symbol"


@dataclass(frozen=True)
class InputToken:
    raw_text: str
    normalized_text: str
    kind: InputTokenKind


@dataclass(frozen=True)
class InputLine:
    raw_text: str
    tokens: Tuple[InputToken, ...]


@dataclass(frozen=True)
class InputBlock:
    raw_text: str
    lines: Tuple[InputLine, ...]


@dataclass(frozen=True)
class InputSpecification:
    blocks: Tuple[InputBlock, ...]
    context_text: str

    @classmethod
    def from_problem_content(
        cls,
        content: ProblemContent,
    ) -> "InputSpecification":
        blocks = content.get_input_format_blocks()

        if not blocks:
            input_format = content.get_input_format()

            if input_format is not None:
                blocks = [input_format]

        return cls(
            blocks=tuple(
                parse_input_block(block)
                for block in blocks
            ),
            context_text=(
                content.get_input_format_context()
            ),
        )


_LATEX_WORD = re.compile(
    r"""
    \\(?:
        mathrm
        |text
        |operatorname
        |rm
        |it
    )
    \s*
    \{
        [^{}]*
    \}
    (?:
        _
        (?:
            \{[^{}]*\}
            |[A-Za-z0-9]+
        )
    )?
    """,
    re.VERBOSE,
)

_INDEXED_WORD = re.compile(
    r"""
    [A-Za-z][A-Za-z0-9]*
    (?:
        _
        (?:
            \{[^{}]*\}
            |\([^()]*\)
            |[A-Za-z0-9]+
        )
    )?
    """,
    re.VERBOSE,
)

_INTEGER = re.compile(
    r"[+-]?[0-9]+"
)

_ELLIPSIS = re.compile(
    r"""
    \\(?:
        ldots
        |cdots
        |dots
        |vdots
        |ddots
    )
    |\.\.\.
    |…
    |‥
    """,
    re.VERBOSE,
)

_DELIMITER = re.compile(
    r"[:,;=()\[\],]"
)

_TOKEN = re.compile(
    "|".join(
        (
            "(?P<LATEX_WORD>{})".format(
                _LATEX_WORD.pattern
            ),
            "(?P<ELLIPSIS>{})".format(
                _ELLIPSIS.pattern
            ),
            "(?P<INTEGER>{})".format(
                _INTEGER.pattern
            ),
            "(?P<WORD>{})".format(
                _INDEXED_WORD.pattern
            ),
            "(?P<DELIMITER>{})".format(
                _DELIMITER.pattern
            ),
            r"(?P<SYMBOL>\S)",
        )
    ),
    re.VERBOSE,
)

_LATEX_WORD_NORMALIZER = re.compile(
    r"""
    \\(?:
        mathrm
        |text
        |operatorname
        |rm
        |it
    )
    \s*
    \{
        (?P<name>[^{}]*)
    \}
    (?P<index>
        (?:
            _
            (?:
                \{[^{}]*\}
                |[A-Za-z0-9]+
            )
        )?
    )
    """,
    re.VERBOSE,
)


def _normalize_latex_word(
    raw_text: str,
) -> str:
    match = _LATEX_WORD_NORMALIZER.fullmatch(
        raw_text
    )

    if match is None:
        return raw_text

    return "{}{}".format(
        match.group("name"),
        match.group("index"),
    )


def _make_token(
    match,
) -> InputToken:
    raw_text = match.group(0)
    group = match.lastgroup

    if group == "LATEX_WORD":
        return InputToken(
            raw_text=raw_text,
            normalized_text=(
                _normalize_latex_word(raw_text)
            ),
            kind=InputTokenKind.WORD,
        )

    if group == "ELLIPSIS":
        return InputToken(
            raw_text=raw_text,
            normalized_text="...",
            kind=InputTokenKind.ELLIPSIS,
        )

    if group == "INTEGER":
        return InputToken(
            raw_text=raw_text,
            normalized_text=raw_text,
            kind=InputTokenKind.INTEGER,
        )

    if group == "WORD":
        return InputToken(
            raw_text=raw_text,
            normalized_text=raw_text,
            kind=InputTokenKind.WORD,
        )

    if group == "DELIMITER":
        return InputToken(
            raw_text=raw_text,
            normalized_text=raw_text,
            kind=InputTokenKind.DELIMITER,
        )

    return InputToken(
        raw_text=raw_text,
        normalized_text=raw_text,
        kind=InputTokenKind.SYMBOL,
    )


def tokenize_input_line(
    line: str,
) -> Tuple[InputToken, ...]:
    return tuple(
        _make_token(match)
        for match in _TOKEN.finditer(line)
    )


def parse_input_block(
    block: str,
) -> InputBlock:
    return InputBlock(
        raw_text=block,
        lines=tuple(
            InputLine(
                raw_text=line,
                tokens=tokenize_input_line(line),
            )
            for line in block.splitlines()
        ),
    )


def normalized_token_lines(
    specification: InputSpecification,
) -> List[List[List[str]]]:
    return [
        [
            [
                token.normalized_text
                for token in line.tokens
            ]
            for line in block.lines
        ]
        for block in specification.blocks
    ]
