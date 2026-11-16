# Development guide

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verification loop (must be green before merge)

```bash
.venv/bin/python -m pytest tests -q     # tests (offline; ~30s)
.venv/bin/ruff check .                  # lint
.venv/bin/ruff format --check .         # formatting (auto-fix: ruff format .)
.venv/bin/mypy                          # type check
```

CI runs the same four checks on ubuntu + macos, Python 3.9–3.13.

## Test markers

| marker | when skipped | purpose |
|---|---|---|
| `network` | unless `ATCODERTOOLS_TEST_NETWORK=1` | hits real atcoder.jp (flaky, rate-limited) |
| `requires_cpp/java/rust/dlang/nim/csharp` | toolchain probe fails | compiles/runs generated code |

Toolchain probes live in `tests/utils/toolchains.py` — extend them when a
new language/compiler is added; the marker→lang map is `MARKER_TO_LANG`
(keep `pyproject.toml` marker names in sync).

`tests/resources/**/*.py` are sample programs executed by the tester as
subprocesses — never pytest tests; do not "fix" or collect them.

## Invariants for reviewers/AI

1. Tests must pass offline on a machine with no compilers and no network.
2. No new deprecation warnings (`filterwarnings = ["error"]` in pytest).
3. Every function has complete type annotations (`disallow_untyped_defs`).
4. Backward compatibility surfaces: CLI flags/exit codes, `metadata.json`,
   `~/.atcodertools.toml` keys, template variables, `code_generator_file`
   plugin signature, `Language` registry fields, `atcodertools.*` import paths.
   See `docs/architecture.md` → Contracts.

## Common tasks

- **Add a language**: extend `ALL_LANGUAGES` in `common/language.py`, add
  `code_generators/<lang>.py` (`main(args: CodeGenArgs) -> str`), add
  `tools/templates/default_template.<ext>`, add toolchain probe + marker,
  regenerate expected-code fixtures.
- **Add a judge type**: extend `JudgeType`/`Judge` in `common/judgetype.py`
  (`verify`, `to_dict`, `from_dict`), dispatch in `tester._decide_judge_method`
  + `ExecResult.is_correct_output` + `Metadata.from_dict` + `setter`.
- **Release**: bump `release_management/version.py`, update CHANGELOG.md,
  tag, `python -m build`, upload to PyPI — then run the
  `.devin/skills/release-verification` checklist.
