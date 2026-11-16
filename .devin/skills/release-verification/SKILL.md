---
name: release-verification
description: Verify a released atcoder-tools version works correctly after publishing to PyPI. Use after every release/tag, or to validate a release candidate before publishing.
---

# Release verification

Goal: confirm the published artifact (not the source tree) actually works
for end users. Run in an isolated environment.

## 1. Install the published artifact in a clean venv

```bash
python3 -m venv /tmp/atc-verify-venv
/tmp/atc-verify-venv/bin/pip install atcoder-tools==<VERSION>
```

## 2. CLI smoke tests (no credentials needed)

```bash
/tmp/atc-verify-venv/bin/atcoder-tools version        # prints <VERSION>, non-fatal PyPI check
/tmp/atc-verify-venv/bin/atcoder-tools gen --help     # each subcommand parses
/tmp/atc-verify-venv/bin/atcoder-tools test --help
/tmp/atc-verify-venv/bin/atcoder-tools submit --help
```

Expected: version prints the released version; `--help` exits 0 for all
subcommands.

## 3. Package contents check

```bash
/tmp/atc-verify-venv/bin/python -c "import atcodertools; print(atcodertools.__file__)"
/tmp/atc-verify-venv/bin/python - <<'EOF'
import importlib.resources as r
files = r.files("atcodertools.tools")
assert (files / "atcodertools-default.toml").is_file()
assert (files / "templates/default_template.cpp").is_file()
assert (files / "templates/judge_program.cpp").is_file()
print("package data OK")
EOF
```

## 4. Offline end-to-end

Pick a fixture problem dir from `tests/resources/test_atcoder_client_mock`
or any dir containing `metadata.json`, `main.cpp`, `in_*.txt`, `out_*.txt`:

```bash
cd <fixture-problem-dir>
/tmp/atc-verify-venv/bin/atcoder-tools test            # expect "PASSED", exit 0
/tmp/atc-verify-venv/bin/atcoder-tools compile         # if a compiler exists
```

## 5. Network-dependent checks (only when atcoder.jp is reachable)

```bash
/tmp/atc-verify-venv/bin/atcoder-tools gen abc<NNN>    # e.g. last ABC
```

Expect: per-problem dirs created with `main.cpp`, `in_*.txt`, `out_*.txt`,
`metadata.json`. 429 responses mean rate limiting, not a release bug —
retry later.

## 6. Report

```
Version: <VERSION>   Install: OK/FAIL   version cmd: OK/FAIL
help xN: OK/FAIL     package data: OK/FAIL   offline test: OK/FAIL
gen (network): OK/FAIL/SKIP(429)
Verdict: release usable | release broken (details)
```
