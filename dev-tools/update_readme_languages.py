#!/usr/bin/env python3
"""Regenerate the supported-languages table in README.md.

The language list is derived automatically from
``atcodertools.common.language.ALL_LANGUAGES``; the README label and the
contributor columns are curated in ``README_LANG_INFO`` below.

Usage:
    python dev-tools/update_readme_languages.py          # rewrite README.md
    python dev-tools/update_readme_languages.py --check  # verify it is fresh
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from atcodertools.common.language import ALL_LANGUAGES  # noqa: E402

README_PATH = REPO_ROOT / "README.md"
BEGIN_MARKER = "<!-- LANGUAGES_TABLE:BEGIN -->"
END_MARKER = "<!-- LANGUAGES_TABLE:END -->"

# Curated README metadata, keyed by Language.name.
# label: how the language is displayed in the README table.
# contributors: list of (github_handle, roles) pairs, in column order.
def _c(handle, roles):
    return "[@{}](https://github.com/{}/) ({})".format(handle, handle, roles)


README_LANG_INFO = {
    "cpp": {
        "label": "C++",
        "contributors": [
            _c("kyuridenamida", "generator, template"),
            _c("asi1024", "template"),
        ],
    },
    "java": {
        "label": "Java",
        "contributors": [
            _c("kyuridenamida", "generator, template"),
        ],
    },
    "rust": {
        "label": "Rust",
        "contributors": [
            _c("fukatani", "generator, template"),
            _c("koba-e964", "template, CR"),
        ],
    },
    "python": {
        "label": "Python3",
        "contributors": [
            _c("kmyk", "generator, template"),
            _c("penpenpng", "generator"),
        ],
    },
    "nim": {
        "label": "Nim",
        "contributors": [
            _c("chaemon", "generator, template"),
        ],
    },
    "d": {
        "label": "D",
        "contributors": [
            _c("penpenpng", "generator, template"),
        ],
    },
    "cs": {
        "label": "C#",
        "contributors": [
            _c("chaemon", "generator, template"),
        ],
    },
    "swift": {
        "label": "Swift",
        "contributors": [
            _c("firewood", "generator, template"),
        ],
    },
    "go": {
        "label": "Go",
        "contributors": [
            _c("nu50218", "generator, template"),
            _c("chaemon", "generator, template"),
        ],
    },
    "julia": {
        "label": "Julia",
        "contributors": [
            _c("yatra9", "generator, template"),
            _c("chaemon", "generator, template"),
        ],
    },
}

MAX_CONTRIBUTOR_COLUMNS = 2


def generate_languages_table():
    lines = [
        "|対応言語  |"
        + "|".join(
            "Contributor {}".format(i + 1)
            for i in range(MAX_CONTRIBUTOR_COLUMNS)
        )
        + "|",
        "|---:|" + ":---:|" * MAX_CONTRIBUTOR_COLUMNS,
    ]
    for lang in ALL_LANGUAGES:
        info = README_LANG_INFO.get(
            lang.name, {"label": lang.display_name, "contributors": []}
        )
        contributors = info["contributors"][:MAX_CONTRIBUTOR_COLUMNS]
        contributors += [""] * (MAX_CONTRIBUTOR_COLUMNS - len(contributors))
        lines.append(
            "|{}|{}|".format(info["label"], "|".join(contributors))
        )
    return "\n".join(lines)


def render_readme(readme_text):
    begin = readme_text.find(BEGIN_MARKER)
    end = readme_text.find(END_MARKER)
    if begin == -1 or end == -1 or end < begin:
        raise RuntimeError(
            "README.md does not contain the {} ... {} markers".format(
                BEGIN_MARKER, END_MARKER
            )
        )
    return (
        readme_text[: begin + len(BEGIN_MARKER)]
        + "\n"
        + generate_languages_table()
        + "\n"
        + readme_text[end:]
    )


def main():
    check_only = "--check" in sys.argv
    readme_text = README_PATH.read_text(encoding="utf-8")
    rendered = render_readme(readme_text)

    if check_only:
        if rendered != readme_text:
            print(
                "README.md languages table is out of date. "
                "Run `python dev-tools/update_readme_languages.py`."
            )
            return 1
        return 0

    if rendered != readme_text:
        README_PATH.write_text(rendered, encoding="utf-8")
        print("README.md languages table updated.")
    else:
        print("README.md languages table is already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
