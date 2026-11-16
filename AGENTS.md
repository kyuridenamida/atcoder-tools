# AGENTS.md

Guidance for AI agents (and humans) working on this repository.

## What this is

`atcoder-tools`: a CLI + Python library that scrapes AtCoder problems,
predicts input formats, generates contest code in 7 languages, and runs
local tests/submissions. Python 3.9+, package layout in `atcodertools/`,
tests in `tests/`. Docs index: `docs/architecture.md`,
`docs/development.md`.

## First: make these green, then make your change

```bash
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/mypy
```

All four must stay green. If `.venv` doesn't exist: `python3 -m venv .venv
&& .venv/bin/pip install -e ".[dev]"`. CI (`.github/workflows/ci.yml`)
runs the same commands — never introduce a check that only you can run.

## Rules

1. **Backward compatibility is the top priority.** Do not break the
   contracts listed in `docs/architecture.md` → "Contracts": CLI
   flags/exit codes, `metadata.json` schema, `~/.atcodertools.toml` keys,
   template variable names, the `code_generator_file` plugin signature
   (`main(args: CodeGenArgs) -> str`), `Language` registry fields, and
   `atcodertools.*` import paths. Deprecate loudly before removing.
   Unsure? Read `.devin/skills/merge-review/SKILL.md` before proposing
   the change.

2. **Tests must run fully offline.** Never add a default test that needs
   network — use `@pytest.mark.network`. Never gate on tool presence via
   `which()` alone — use `tests/utils/toolchains.py` probes + the
   `requires_<lang>` markers. `tests/resources/**/*.py` are subprocess
   fixtures, not tests.

3. **Type everything.** `disallow_untyped_defs` is enforced. `Optional`
   for anything that can be `None`. Public API signatures must reflect
   what runtime actually accepts (e.g. `submit_source_code` accepts both
   `Language` and `str` for legacy reasons).

4. **Don't fix warnings by silencing them** — pytest runs with
   `filterwarnings = ["error"]`; fix the deprecated API / resource leak.

5. **Don't reformat untouched code.** Ruff handles style; large diffs
   hiding a small fix will be rejected.

6. **Preserve semantics of `atcoder_tools.py` dispatch**: `test` must
   return non-zero on failure, `-u/--unlock-safety` must gate `submit`,
   `--save-no-session-cache` must not write session files.

## Useful pointers

- Singleton `AtCoderClient` — restore `_request` in tests
  (`restore_client_after_run` in `tests/test_atcoder_client_mock.py`).
- `Format[T]`/`Pattern[T]` generics in `fmtprediction/models/format.py`
  — understand them before touching prediction code.
- `RunConfig` (`[<lang>.run]` TOML section) is parsed but unused —
  intentional; see architecture.md.
- webapp/ is a legacy CRA site, outside the Python harness.

## Merging & releasing

- Before merging: `.devin/skills/merge-review/SKILL.md` checklist.
- After releasing: `.devin/skills/release-verification/SKILL.md`
  checklist.
