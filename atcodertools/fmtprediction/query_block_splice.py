"""クエリ行の書式が別ブロックに書かれた入力形式を、既存の予測経路へ差し戻す。

AtCoderの一部の問題は、入力形式を2つのブロックに分けて記述する。

    ブロック0:  N Q            ブロック1:  l r
                A_1 ... A_N
                \\mathrm{query}_1
                \\vdots
                \\mathrm{query}_Q

このとき ``\\mathrm{query}_k`` は変数ではなくプレースホルダなので、既存の
tokenizerはクエリ行の変数を認識できない。ブロック1をプレースホルダ行へ
展開して1つのブロックへ戻せば、

    N Q
    A_1 ... A_N
    l_1 r_1
    \\vdots
    l_Q r_Q

となり、既存の ``Format`` / ``ParallelPattern`` の語彙でそのまま表現できる。
つまりこれはデータモデルの問題ではなくテキスト解析の問題であり、専用の
中間形式を持ち込まなくても、全言語のコード生成をそのまま利用できる。
"""

import re
from typing import List, Optional, Tuple

from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.fmtprediction.tagged_query import (
    _COMPARISON_PATTERN,
    _IDENTIFIER_PATTERN,
    _PLACEHOLDER_BASES,
    _TOKEN_PATTERN,
    _normalize_block,
)

MAX_QUERY_ARGUMENTS = 6

MIN_PLACEHOLDER_LINES = 2

# ``query_1`` ``Query_Q`` のように、添字が1つだけ付いた単独の語。
_INDEXED_WORD_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9]*)_([A-Za-z0-9]+)$"
)


# ``X_i`` の ``i`` のように、行番号を表す添字。展開時に実際の行番号へ置き換わる。
_ROW_INDEX_NAMES = {"i", "j", "k"}


def _base_name(token: str) -> Optional[str]:
    """引数名を、行番号の添字を付けられる識別子へ正規化する。

    ``X_i`` → ``X``（``i`` は行番号なので落とす）
    ``h_1`` → ``h1``（``1`` は名前の一部なので潰して残す）
    """
    head, _, tail = token.partition("_")

    if not tail or tail in _ROW_INDEX_NAMES:
        name = head
    else:
        name = token.replace("_", "")

    if _IDENTIFIER_PATTERN.fullmatch(name) is None:
        return None

    return name


def _argument_names(block: str) -> Optional[Tuple[str, ...]]:
    """クエリ1行分の書式を定義したブロックから、引数名を取り出す。"""
    if _COMPARISON_PATTERN.search(block):
        # ``1 \leq l \leq r`` のような制約文はクエリ定義ではない。
        return None

    rows = [
        _TOKEN_PATTERN.findall(line)
        for line in _normalize_block(block).splitlines()
    ]
    rows = [row for row in rows if row]

    if len(rows) != 1:
        return None

    names = []

    for token in rows[0]:
        base = _base_name(token)

        if base is None:
            return None

        names.append(base)

    if not 1 <= len(names) <= MAX_QUERY_ARGUMENTS:
        return None

    if len(names) != len(set(names)):
        return None

    return tuple(names)


def _placeholder_index(line: str) -> Optional[str]:
    """プレースホルダ行なら添字を返す。それ以外は None。"""
    normalized = " ".join(_normalize_block(line).split())
    match = _INDEXED_WORD_PATTERN.fullmatch(normalized)

    if match is None:
        return None

    if match.group(1).lower() not in _PLACEHOLDER_BASES:
        return None

    return match.group(2)


def _expand(block: str, names: Tuple[str, ...]) -> Optional[str]:
    lines: List[str] = []
    expanded = 0

    for line in block.splitlines():
        index = _placeholder_index(line)

        if index is None:
            lines.append(line)
            continue

        lines.append(
            " ".join(
                "{}_{}".format(name, index) for name in names
            )
        )
        expanded += 1

    if expanded < MIN_PLACEHOLDER_LINES:
        return None

    return "\n".join(lines)


def splice_query_definition_block(
    content: ProblemContent,
) -> Optional[ProblemContent]:
    """クエリ定義ブロックを展開した ProblemContent を返す。該当しなければ None。"""
    blocks = content.get_input_format_blocks()

    if len(blocks) != 2:
        return None

    names = _argument_names(blocks[1])

    if names is None:
        return None

    spliced = _expand(blocks[0], names)

    if spliced is None:
        return None

    return ProblemContent(
        input_format_text=spliced,
        samples=content.get_samples(),
        original_html=content.original_html,
        input_format_blocks=[spliced],
        input_format_context_text=content.input_format_context_text,
    )
