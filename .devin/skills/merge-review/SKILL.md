---
name: merge-review
description: Review a proposed change for merge-safety in this repo, with strict attention to backward compatibility. Use before merging any PR or committing a non-trivial change.
---

# Merge review

Goal: decide "merge / request changes / reject" for a change to
atcoder-tools, where breaking existing users is the worst outcome.

## Step 0 — Mechanical gates (must all pass)

```bash
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/mypy
git diff origin/master...HEAD --stat   # sanity: scope of the change
```

## Step 1 — Backward-compatibility audit

For each surface below, check whether the diff touches it. Any change
without an explicit deprecation path = **request changes**.

1. **CLI**: subcommand names, flag spellings, defaults, exit codes
   (0/1/255), stdout/stderr formats that scripts may parse.
2. **metadata.json**: key names, value types, `judge_type` enum values.
   A `Metadata.load_file` written by an older version must still work.
3. **~/.atcodertools.toml**: key names/semantics in every section;
   precedence order (common < language < CLI args).
4. **Templates**: exported variable names in `codegen/template_engine.py`
   `render()` kwargs and `codegen_command.py` main.
5. **Plugin API**: `code_generator_file` modules need `main(args)->str`.
6. **Language registry**: `ALL_LANGUAGES` names, `submission_lang_pattern`
   (verify against real AtCoder options before changing!).
7. **Python API**: `atcodertools.*` imports, public signatures — only
   widen (e.g. `Language | str`), never narrow.
8. **Generated code**: changes to templates/generators alter every
   generated file — is that intended? Check `tests/resources/**/expected_*`.
9. **Config file paths**: `~/.atcodertools.toml`,
   `~/.local/share/atcoder-tools/`, `~/atcoder-workspace` defaults.

## Step 2 — Correctness checks

- New/changed behavior has tests; bug fixes have a *regression* test that
  fails on the old code.
- `os.chdir`, singleton mutation (`AtCoderClient._request`), global cwd —
  restored after the test/code path?
- Warning-free under `filterwarnings=["error"]` — no new deprecated APIs,
  no unclosed files.
- `Optional`/type annotations reflect actual `None` usage.
- `type=bool` in argparse is a known bug pattern — use `str_to_bool`.
- Mutable default args (`= []`, `= {}`, `= NormalJudge()`) — use `None`.

## Step 3 — Risk calls

- Network tests added to the default suite → reject (flaky CI).
- Behavior changes hidden inside refactors → reject.
- "README says X but code does Y" → document or flag; never silently
  change behavior to match docs (e.g. `[<lang>.run]` is intentionally
  unused).
- Large formatting diffs touching unmodified logic → reject.

## Verdict template

```
Verdict: merge | request changes | reject
Compat risk: none | low | HIGH  (surfaces touched: ...)
Missing: tests / annotations / docs / deprecation path
Notes: ...
```
