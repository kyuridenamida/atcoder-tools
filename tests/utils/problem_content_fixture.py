import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.client.models.sample import Sample


SCHEMA_VERSION = 1
CONTENT_FILE_NAME = "problem_content.json"
LEGACY_FORMAT_FILE_NAME = "format.txt"
LEGACY_SAMPLE_PATTERN = re.compile(
    r"^ex_(\d+)\.txt$"
)


def _sample_output(sample):
    get_output = getattr(
        sample,
        "get_output",
        None,
    )

    if get_output is not None:
        return get_output()

    return getattr(
        sample,
        "output",
        None,
    )


def problem_content_to_payload(
    content: ProblemContent,
    source: Optional[
        Dict[str, object]
    ] = None,
) -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "input_format_text": (
            content.get_input_format()
        ),
        "input_format_blocks": (
            content.get_input_format_blocks()
        ),
        "input_format_context_text": (
            content.input_format_context_text
        ),
        "samples": [
            {
                "input": sample.get_input(),
                "output": _sample_output(sample),
            }
            for sample in content.get_samples()
        ],
        "source": source or {},
    }


def write_problem_content_fixture(
    case_dir,
    content: ProblemContent,
    source: Optional[
        Dict[str, object]
    ] = None,
) -> Path:
    case_path = Path(case_dir)
    case_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        case_path / CONTENT_FILE_NAME
    )
    temporary_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            problem_content_to_payload(
                content,
                source=source,
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)

    return output_path


def read_problem_content_payload(
    case_dir,
) -> Dict[str, object]:
    path = Path(case_dir) / CONTENT_FILE_NAME
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if (
        payload.get("schema_version")
        != SCHEMA_VERSION
    ):
        raise ValueError(
            "unsupported problem-content "
            "fixture schema"
        )

    for key in (
        "input_format_text",
        "input_format_blocks",
        "input_format_context_text",
        "samples",
    ):
        if key not in payload:
            raise ValueError(
                "problem-content fixture "
                "misses {}".format(key)
            )

    if not isinstance(
        payload["input_format_blocks"],
        list,
    ):
        raise ValueError(
            "input_format_blocks must be a list"
        )

    if not isinstance(
        payload["samples"],
        list,
    ):
        raise ValueError(
            "samples must be a list"
        )

    return payload


def _content_from_payload(
    payload: Dict[str, object],
) -> ProblemContent:
    samples: List[Sample] = []

    for item in payload["samples"]:
        if not isinstance(item, dict):
            raise ValueError(
                "sample entry must be an object"
            )

        samples.append(
            Sample(
                item["input"],
                item.get("output"),
            )
        )

    return ProblemContent(
        input_format_text=payload[
            "input_format_text"
        ],
        input_format_blocks=payload[
            "input_format_blocks"
        ],
        input_format_context_text=payload[
            "input_format_context_text"
        ],
        samples=samples,
    )


def _read_legacy_problem_content(
    case_dir,
) -> ProblemContent:
    case_path = Path(case_dir)

    input_format = (
        case_path
        / LEGACY_FORMAT_FILE_NAME
    ).read_text(
        encoding="utf-8"
    )

    sample_paths = []

    for path in case_path.iterdir():
        match = LEGACY_SAMPLE_PATTERN.match(
            path.name
        )

        if match is not None:
            sample_paths.append(
                (
                    int(match.group(1)),
                    path,
                )
            )

    samples = [
        Sample(
            path.read_text(
                encoding="utf-8"
            ),
            None,
        )
        for _, path in sorted(sample_paths)
    ]

    return ProblemContent(
        input_format,
        samples,
    )


def read_problem_content_fixture(
    case_dir,
) -> ProblemContent:
    case_path = Path(case_dir)

    if (
        case_path / CONTENT_FILE_NAME
    ).is_file():
        return _content_from_payload(
            read_problem_content_payload(
                case_path
            )
        )

    return _read_legacy_problem_content(
        case_path
    )


def is_problem_content_fixture(
    case_dir,
) -> bool:
    case_path = Path(case_dir)

    return (
        case_path.is_dir()
        and (
            (
                case_path
                / CONTENT_FILE_NAME
            ).is_file()
            or (
                case_path
                / LEGACY_FORMAT_FILE_NAME
            ).is_file()
        )
    )
