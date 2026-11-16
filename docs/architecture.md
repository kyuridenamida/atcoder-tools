# Architecture

`atcoder-tools` has one pipeline: **fetch problem → predict format/constants →
generate code → run/judge/submit**. Each stage maps to one package.

## Module map

```
atcoder_tools.py            CLI entry: gen | test | submit | compile | set | codegen | version

atcodertools/
├── client/                 HTTP layer + HTML parsing
│   ├── atcoder.py          AtCoderClient (requests.Session, login, download, submit)
│   └── models/             Contest, Problem, ProblemContent, Sample, Submission
│
├── fmtprediction/          Input-format inference (the "brain")
│   ├── tokenize_format.py  FormatSearcher: DFS over token splits, min-var pruning
│   ├── predict_simple_format.py  variable tokens -> Format[SimpleVariable] (loop detection)
│   ├── predict_types.py    Format + sample inputs -> per-variable Type (int/float/str)
│   ├── predict_format.py   pipeline entry: ProblemContent -> FormatPredictionResult
│   ├── token_manager.py    mutable cursor used by the DFS and the type predictor
│   └── models/             CalcNode (arithmetic expr parse/eval/simplify), Index,
│                           Variable, VariableToken, Type, Format/Pattern, result
│
├── constprediction/        constants_prediction.py: HTML -> ProblemConstantSet
│                           (mod value, yes/no strings, judge method)
│
├── codegen/                FormatPredictionResult -> source code per language
│   ├── code_generators/    cpp|java|rust|python|nim|d|cs; each main(args)->str
│   ├── template_engine.py  Jinja2 render + legacy ${} fallback (deprecated)
│   ├── code_style_config.py CodeStyleConfig incl. custom code_generator_file loading
│   └── models/code_gen_args.py  CodeGenArgs (template, format, constants, config)
│
├── tools/                  subcommand implementations
│   ├── envgen.py           gen: contest -> problem dirs, samples, code, metadata.json
│   ├── tester.py           test: run exec file on in_*.txt/out_*.txt, judge output
│   ├── submit.py           submit: local test -> safety check -> upload
│   ├── setter.py           set: rewrite metadata.json (judge type, lang, error value)
│   ├── compiler.py         compile: run lang.compile_command for main (+judge)
│   ├── models/metadata.py  metadata.json schema (problem, code_filename, patterns, lang, judge)
│   └── templates/          default code templates + default judge program (cpp)
│
├── config/                 ~/.atcodertools.toml loading & layering
│   └── config.py           precedence: common < lang-specific < CLI args
│
├── executils/              run_program (subprocess+timeout), run_command (shell)
├── fileutils/              workspace file creation, cache dir (~/.local/share/atcoder-tools)
├── common/                 Language registry (ALL_LANGUAGES), Judge types, logger
└── release_management/     __version__, PyPI latest-version check
```

## Data flow

- `gen`: AtCoderClient -> ProblemContent -> `predict_format` +
  `predict_constants` -> `code_generator(CodeGenArgs)` -> `create_code` +
  `Metadata.save_to(metadata.json)`
- `test`: metadata.json + config -> exec file -> `run_program` per sample ->
  `Judge.verify` (or external judge program for multisolution/interactive)
- `codegen`: same prediction pipeline as `gen`, prints to stdout
- `submit`: `test` passes -> `download_submission_list` safety check ->
  `submit_source_code`

## Contracts that must not break silently

- **CLI**: subcommands, flags, exit codes (0 = pass, non-0 = fail), `-u` safety.
- **`metadata.json`**: keys `problem{contest{contest_id},problem_id,alphabet}`,
  `code_filename`, `sample_in_pattern`, `sample_out_pattern`, `lang`, `judge`
  (`judge_type` ∈ normal|decimal|multisolution|interactive, plus decimal's
  `error_type`/`diff`).
- **`~/.atcodertools.toml`**: `[codestyle]`, `[postprocess]`, `[etc]`,
  `[<lang>.<category>]` layering; CLI args override everything.
- **Template variables**: `prediction_success`, `input_part`,
  `formal_arguments`, `actual_arguments`, `mod`, `yes_str`, `no_str`,
  `atcodertools.{version,url}`. Custom user templates and
  `code_generator_file` plugins (`main(args: CodeGenArgs) -> str`) depend on
  these names.
- **`Language` registry**: `name`, `extension`, `submission_lang_pattern`
  (must match an option on the real AtCoder submit page), `compile_command`,
  `test_command` with `{filename}`/`{exec_filename}`/`{capitalized_filename}`
  placeholders.
- **Python API**: `atcodertools.*` is a public library used by external tools;
  keep import paths stable.

## Known limitations (documented, not bugs-to-fix-silently)

- `[<lang>.run]` (`run_config`) is parsed but **not consumed** by
  tester/compiler — wiring it changes user-visible behavior; decide in an
  issue first.
- `AtCoderClient` is a singleton by design; tests must restore `_request`
  (see `restore_client_after_run`).
- webapp/ is a legacy Create-React-App analysis site, independent of the
  Python package; not covered by the Python test/lint/type harness.
