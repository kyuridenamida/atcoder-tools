[![Build Status](https://api.travis-ci.org/kyuridenamida/atcoder-tools.svg?branch=stable)](https://travis-ci.org/kyuridenamida/atcoder-tools)
[![codecov](https://codecov.io/gh/kyuridenamida/atcoder-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/kyuridenamida/atcoder-tools)
[![PyPI](https://img.shields.io/pypi/v/atcoder-tools.svg)](https://pypi.python.org/pypi/atcoder-tools)

AtCoder Tools
====
Python 3.6 以降で動作する [AtCoder](https://atcoder.jp/) からサンプル入力をダウンロードしたりする際に便利なツールです。

このツールには次のような機能があります。
- AtCoderへのログイン，入出力例データなどの抽出
- 枝刈り探索による高精度・高速な入力フォーマット解析 (ARC、ABC、AGCについては約9割ほど)
- 問題文中に含まれるMOD値、YES/NO文字列、誤差ジャッジのための誤差値等の定数値抽出
- サンプルのローカルテスト機能
    - 誤差ジャッジに対応 by [@chaemon](https://github.com/chaemon/)
- コード提出機能
- 入力フォーマット解析結果や抽出した定数値を用いたテンプレートからのコード自動生成(以下の表に記載されている言語をサポートしています)
    - カスタムテンプレートに対応
    - 他言語対応のためのコントリビューション(≒中間形式からコードに変換する部分のPR)を募集中です!

|対応言語  |Contributor 1|Contributor 2|
|---:|:---:|:---:|
|C++|[@kyuridenamida](https://github.com/kyuridenamida/) (generator, template)|[@asi1024](https://github.com/asi1024/) (template)|
|Java|[@kyuridenamida](https://github.com/kyuridenamida/) (generator, template)||
|Rust|[@fukatani](https://github.com/fukatani/) (generator, template)|[@koba-e964](https://github.com/koba-e964/) (template, CR)|
|Python3|[@kmyk](https://github.com/kmyk/) (generator, template)|[@penpenpng](https://github.com/penpenpng/) (generator)|
|D|[@penpenpng](https://github.com/penpenpng/) (generator, template)||
|Nim|[@chaemon](https://github.com/chaemon/) (generator, template)||
|C#|[@chaemon](https://github.com/chaemon/) (generator, template)||
|Swift|[@firewood](https://github.com/firewood/) (generator, template)||

## Demo
<img src="https://user-images.githubusercontent.com/233559/52807100-f6e2d300-30cd-11e9-8906-82b9f9b2dff7.gif" width=70%>

## How to install
`pip3 install atcoder-tools` 

ただの`pip`だとPython 2系を使ってインストールされる可能性があるためうまくいかないかもしれません。

## Userscript by [@kmyk](https://github.com/kmyk/) (NEW! 2019/03/06)
Tampermonkey(各種ブラウザで動作)でインストールすることが可能なUserscriptです。公開されている過去問を対象として、atcoder-toolsで自動生成されたコードをそのままAtCoderのスニペット上で利用できます。
1. Tampermonkey をインストールする ([Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo), [FireFox](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/))
2. https://kyuridenamida.github.io/atcoder-tools/index.user.js にアクセスしてUserscriptをインストール
3. ログインした状態で適当な問題ページに行く(e.g. https://atcoder.jp/contests/abc120/tasks/abc120_d)
4. 正しくインストールされている場合、ページ下部のコードスニペットにコードが標準で埋め込まれている (atcoder-toolsの対応言語のみ)
<img src="https://user-images.githubusercontent.com/233559/53821542-56d3e780-3fb1-11e9-89d9-24a3d0e9af5c.png" width=50%>

## Analysis
https://kyuridenamida.github.io/atcoder-tools/

各問題ごとの解析結果などが載っています。

## Usage


*重要: かつてパスワード入力なしでログインを実現するために`AccountInformation.py`にログイン情報を書き込むことを要求していましたが、セキュリティリスクが高すぎるため、セッション情報のみを保持する方針に切り替えました。
今後はできるだけ保持されているセッション情報を利用してAtCoderにアクセスし、必要に応じて再入力を要求します。
過去のユーザーの皆様には`AccountInformation.py`を削除して頂くようお願い申し上げます。*


- `atcoder-tools gen {contest_id}` コンテスト環境を用意します。
- `atcoder-tools test` カレント・ディレクトリ上に実行ファイルと入出力(in_\*.txt, out_\*.txt)がある状態で実行するとローカルテストを行います。
- `atcoder-tools submit` カレント・ディレクトリ上で実行すると対応する問題がサンプルに通る場合ソースコードを提出します。既にAtCoder上にその問題に対する提出がある場合、`-u`を指定しないと提出できないようになっています。
- `atcoder-tools version` 現在の atcoder-tools のバージョンを出力します。

`atcoder-tools gen --help`で`atcoder-tools gen`の引数の詳細について確認することができます。

例: 
```console
atcoder-tools gen agc001
cd ~/atcoder-workspace/agc001/A
g++ main.cpp
atcoder-tools test
```

`--without-login` 引数を指定するとログインなしでデータをダウンロードできます(一般公開されているコンテストのみ)。

```console
$ atcoder-tools gen  [contest_id] --without-login
```

### gen の詳細
```
usage: atcoder-tools gen
       [-h] [--without-login] [--workspace WORKSPACE] [--lang LANG]
       [--template TEMPLATE] [--parallel] [--save-no-session-cache]
       [--skip-existing-problems] [--config CONFIG]
       contest_id

positional arguments:
  contest_id            Contest ID (e.g. arc001)

optional arguments:
  -h, --help            show this help message and exit
  --without-login       Download data without login
  --workspace WORKSPACE
                        Path to workspace's root directory. This script will create files in {WORKSPACE}/{contest_name}/{alphabet}/ e.g. ./your-workspace/arc001/A/
                        [Default] /home/kyuridenamida/atcoder-workspace
  --lang LANG           Programming language of your template code, cpp or java or rust or python or nim or d or cs or julia.
                        [Default] cpp
  --template TEMPLATE   File path to your template code
                        [Default (C++)] /atcodertools/tools/templates/default_template.cpp
                        [Default (Java)] /atcodertools/tools/templates/default_template.java
                        [Default (Rust)] /atcodertools/tools/templates/default_template.rs
                        [Default (Python3)] /atcodertools/tools/templates/default_template.py
                        [Default (NIM)] /atcodertools/tools/templates/default_template.nim
                        [Default (D)] /atcodertools/tools/templates/default_template.d
                        [Default (C#)] /atcodertools/tools/templates/default_template.cs
  --parallel            Prepare problem directories asynchronously using multi processors.
  --save-no-session-cache
                        Save no session cache to avoid security risk
  --skip-existing-problems
                        Skip processing every problem for which a directory already exists
  --config CONFIG       File path to your config file
                        [Default (Primary)] /home/kyuridenamida/.atcodertools.toml
                        [Default (Secondary)] /atcoder-tools/atcodertools/tools/atcodertools-default.toml
```

### test の詳細

```
usage: atcoder-tools test [-h] [--exec EXEC] [--num NUM]
                                         [--dir DIR] [--timeout TIMEOUT]
                                         [--knock-out]
                                         [--skip-almost-ac-feedback]
                                         [--judge-type JUDGE_TYPE]
                                         [--error-value ERROR_VALUE]

optional arguments:
  -h, --help            show this help message and exit
  --exec EXEC, -e EXEC  File path to the execution target. [Default] Automatically detected exec file
  --num NUM, -n NUM     The case number to test (1-origin). All cases are tested if not specified.
  --dir DIR, -d DIR     Target directory to test. [Default] Current directory
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout for each test cases (sec) [Default] 1
  --knock-out, -k       Stop execution immediately after any example's failure [Default] False
  --skip-almost-ac-feedback, -s
                        Hide inputs and expected/actual outputs if result is correct and there are error outputs [Default] False,
  --judge-type JUDGE_TYPE, -j JUDGE_TYPE
                        error type must be one of [normal, absolute, relative, absolute_or_relative]
  --error-value ERROR_VALUE, -v ERROR_VALUE
                        error value for decimal number judge: [Default] 0.000000001
```


### submit の詳細

```
usage: atcoder-tools submit [-h] [--exec EXEC] [--dir DIR]
                                           [--timeout TIMEOUT] [--code CODE]
                                           [--force] [--save-no-session-cache]
                                           [--unlock-safety]
                                           [--judge-type JUDGE_TYPE]
                                           [--error-value ERROR_VALUE]

optional arguments:
  -h, --help            show this help message and exit
  --exec EXEC, -e EXEC  File path to the execution target. [Default] Automatically detected exec file
  --dir DIR, -d DIR     Target directory to test. [Default] Current directory
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout for each test cases (sec) [Default] 1
  --code CODE, -c CODE  Path to the source code to submit [Default] Code path written in metadata.json
  --force, -f           Submit the code regardless of the local test result [Default] False
  --save-no-session-cache
                        Save no session cache to avoid security risk
  --unlock-safety, -u   By default, this script only submits the first code per problem. However, you can remove the safety by this option in order to submit codes twice or more.
  --judge-type JUDGE_TYPE, -j JUDGE_TYPE
                        error type must be one of [normal, absolute, relative, absolute_or_relative]
  --error-value ERROR_VALUE, -v ERROR_VALUE
                        error value for decimal number judge: [Default] 1e-09
```

### codegen の詳細

```
usage: ./atcoder-tools codegen [-h] [--without-login] [--lang LANG]
                               [--template TEMPLATE] [--save-no-session-cache]
                               [--config CONFIG]
                               url

positional arguments:
  url                   URL (e.g. https://atcoder.jp/contests/abc012/tasks/abc012_3)

optional arguments:
  -h, --help            show this help message and exit
  --without-login       Download data without login
  --lang LANG           Programming language of your template code, cpp or java or rust.
                        [Default] cpp
  --template TEMPLATE   File path to your template code
                        [Default (C++)] /home/user/GitHub/atcoder-tools/atcodertools/tools/templates/default_template.cpp
                        [Default (Java)] /home/user/GitHub/atcoder-tools/atcodertools/tools/templates/default_template.java
                        [Default (Rust)] /home/user/GitHub/atcoder-tools/atcodertools/tools/templates/default_template.rs
  --save-no-session-cache
                        Save no session cache to avoid security risk
  --config CONFIG       File path to your config file
                        [Default (Primary)] /home/user/.atcodertools.toml
                        [Default (Secondary)] /home/user/GitHub/atcoder-tools/atcodertools/tools/atcodertools-default.toml
```


## 設定ファイルの例
`~/.atcodertools.toml`に以下の設定を保存すると、コードスタイルや、コード生成後に実行するコマンドを指定できます。

以下は、次の挙動を期待する場合の`~/.atcodertools.toml`の例です。

- `indent_type='space'` スペースがインデントに使われる(`'tab'`を指定した場合はタブが使われる)
- `indent_width=4` インデント幅は4である (`indent_width`が無指定の場合`4`(nim言語以外), `2`(nim言語)が規定値として使われます。)
- `template_file='~/my_template.cpp'` コード生成テンプレートとして`~/my_template.cpp`を使う
- `workspace_dir='~/atcoder-workspace/'` ワークスペースのルートは `~/atcoder-workspace/`
- `lang='cpp'` 言語設定は `cpp` (提出時もしくはデフォルトのコードジェネレーター生成時に使われます)
- `code_generator_file="~/custom_code_generator.py"` カスタムコードジェネレーター `~/custom_code_generator.py`を指定する
- `code_generator_toml="~/universal_code_generator.toml"` ユニバーサルコードジェネレーター `~/universal_code_generator.toml`を指定する
- `exec_on_each_problem_dir='clang-format -i ./*.cpp'` `exec_on_contest_dir='touch CMakeLists.txt'`
    - 問題用ディレクトリ内で毎回`clang-format`を実行して、最後に`CMakeLists.txt`(空)をコンテスト用ディレクトリに生成する

- `compile_before_testing` テスト前にコンパイルを実行するか否かをTrue/Falseで指定。何も指定しないとFalseとなります。
- `compile_only_when_diff_detected` テスト前のコンパイルの際、元のソースに変更があった場合のみ実行するかをTrue/Falseで指定。何も指定しないとFalseとなります。

なお、`compile_before_testing`, `compile_only_when_diff_detected`はいずれもtesterの引数で指定することも可能で、指定した場合はそちらが優先されます。

- `download_without_login=false` AtCoderにログインせずにダウンロードを行う機能を使わない (公開コンテストに対してのみ可能)
- `parallel_download=false` データの並列ダウンロードを無効にする
- `save_no_session_cache=false` ログイン情報のクッキーを保存する
- `skip_existing_problems=false` ディレクトリが既に存在する問題の処理をスキップする
- `in_example_format="in_{}.txt"` テストケース(input)のフォーマットを`in_1.txt, in_2.txt, ...`とする
- `out_example_format="out_{}.txt"` テストケース(output)のフォーマットを`out_1.txt, out_2.txt, ...`とする

```toml
[codestyle]
indent_type='space' # 'tab' or 'space'
indent_width=4
template_file='~/my_template.cpp'
workspace_dir='~/atcoder-workspace/'
lang='cpp' # Check README.md for the supported languages.
code_generator_file="~/custom_code_generator.py"
[postprocess]
exec_on_each_problem_dir='clang-format -i ./*.cpp'
exec_on_contest_dir='touch CMakeLists.txt'
[compiler]
compile_command='g++ main.cpp -o main -std=c++17'
compile_only_when_diff_detected=true
[tester]
compile_before_testing=true
compile_only_when_diff_detected=true
[etc]
download_without_login=false
parallel_download=false
save_no_session_cache=false
skip_existing_problems=false
in_example_format="in_{}.txt"
out_example_format="out_{}.txt"

```

### カスタムコードジェネレーター
[標準のC++コードジェネレーター](https://github.com/kyuridenamida/atcoder-tools/blob/master/atcodertools/codegen/code_generators/cpp.py)に倣って、
`(CogeGenArgs) -> str(ソースコード)`が型であるような`main`関数を定義した.pyファイルを`code_generator_file`で指定すると、コード生成時にカスタムコードジェネレーターを利用できます。


### ユニバーサルコードジェネレーター
ユニバーサルコードジェネレーターはループ・配列アクセス方法等のいくつかの言語仕様を記述するだけでカスタムコードジェネレーターよりも簡単にコード生成することを意図して作成したジェネレーターです。設定ファイルの`code_generator_toml`で指定します。書き方は以下です。

- *base_indent* 入力部分のインデント数
- *insert_space_around_operators* 入力部分の変数や演算子の間にスペースを入れるかどうかをtrue/falseで指定
- *newline_after_input* 入力部分で入力ごとに空行を入れるかどうかをtrue/falseで指定
- *global_prefix* グローバル変数の宣言時に入れる接頭辞(Javaなどでstaticを指定したりできます)

以下のようにテーブルを定義します。各項目はダブルコーテーションあるいはシングルコーテーションを用いた文字列で指定します。Pythonのformatメソッドに渡されるため、波括弧等の文字を直に書きたい場合はエスケープする必要があります。
テーブルのキーは整数(int), 浮動小数(float), 文字列(str), およびこれら3つを使った1次元配列(seq), 2次元配列(2d_seq)となっています。

- *[index]* ループインデックスの名称を指定します。１重目を`i`, 2重目を`j`で指定してください。省略可能で省略した場合はi, jが指定されます。Perl, PHPなどの言語で$i, $jなどとi, j以外の名前を指定しなければならないとき用のつもりです。
- *[loop]* ループに関することを記述します
    - **header** ループの最初に記述する内容。ループを回すための変数は`{loop_var}`, 回す回数は`{length}`を用いてください。
    - **footer** ループの最後に記述する内容。C++, Javaでは閉じカッコになります。波括弧の場合は`}}`とエスケープする必要があることに注意してください。
- *[type]* タイプ(int, float, str)のタイプについて記述します。例を参照してください。
- *[default]* デフォルトの値について記述します。例を参照してください。注意: TOMLの表記に癖があるようで、ダブルコーテーション2つ(空の文字列)を表記する際にはstr='""'とするとよいようです。"\"\""だとエラーになるようです。
- *[input_func]* int, float, strについて入力時に呼び出す関数を記述します。
- *[arg]* solve関数の引数の記述方法について指定します。`int`, `float`, `str`, `seq`, `2d_seq`について記述してください。`{name}`が変数名, `{type}`が`seq`, `2d_seq`についてベースとなる型です。
- *[actual_arg]* `seq`, `2d_seq`についてsolve関数を呼び出す際の引数の渡し方について記述します。C++などでmoveをつかってメモリを節約したいときなどに指定できます。省略可能で、省略した場合はそのまま渡されます。

- *[access]* 配列のアクセス方法について記述します。`seq`, `2d_seq`について指定してください。`{name}`で変数名, `{index_i}`, `{index_j}`でインデックス名を指定します。


以下は宣言・確保・入力を行うためのコードを記述します。いくつかを同時に行う方法も指定できます。いずれも一行または複数行に渡る指定が可能でセミコロン等の終端子も(必要な言語では)記述してください。
キーワードとして`{name}`, `{type}`はそれぞれ対象となる変数名、タイプ名で、上記で指定した`{default}`が使えます。また、指定していれば`{input_func}`も使えます。`seq`, `2d_seq`の場合は`{type}`はベースとなる型名になります(`vector<int>`における`int`)のでご注意ください。また、`seq`の長さは`{length}`, `2d_seq`の長さは`{length_i}`, `{length_j}`となっています。

- *[declare]* int, float, str, seq, 2d_seqの宣言方法について記述します。
- *[allocate]* `seq`, `2d_seq`の確保の方法を記述します。
- *[declare_and_allocate]* `seq`, `2d_seq`について宣言と確保を同時に行う方法について記述します。
- *[input]* int, float, strの入力方法について記述します。

以下は入力コードの冗長性を下げる目的で指定するテーブルで省略可能なものです。指定方法についてはPythonの設定を参照してください。

- *[allocate_and_input]* `seq`, `2d_seq`について確保と入力をまとめて行うことができる場合に記述します。省略した場合、上記で指定した確保と入力の方式を複合したものが挿入されます
- *[declare_and_allocate_and_input]* `seq`, `2d_seq`について宣言・確保・入力をまとめて行うことができる場合に記述します。省略した場合、上記で指定した宣言と確保と入力の方式を複合したものが挿入されます

例えばC++での設定方法は以下です。
```toml
base_indent = 1
insert_space_around_operators = false

# global変数宣言時の接頭辞
global_prefix = ""

# ループ
[loop]
header = "for(int {loop_var} = 0 ; {loop_var} < {length} ; {loop_var}++){{"
footer = "}}"

# タイプ
[type]
int = "long long"
float = "long double"
str = "std::string"

# デフォルト値
[default]
int = "0"
float = "0.0"
str = '""'

# 引数
[arg]
int = "long long {name}"
float = "long double {name}"
str = "std::string {name}"
seq = "std::vector<{type}> {name}"
2d_seq = "std::vector<std::vector<{type}>> {name}"

# 引数への渡し方
[actual_arg]
seq = "std::move({name})"
2d_seq = "std::move({name})"

# 配列アクセス
[access]
seq = "{name}[{index}]"
2d_seq = "{name}[{index_i}][{index_j}]"

# 宣言
[declare]
int = "long long {name};"
float = "long double {name};"
str = "std::string {name};"
seq = "std::vector<{type}> {name};"
2d_seq = "std::vector<std::vector<{type}>> {name};"

# 確保
[allocate]
seq = "{name}.assign({length}, {default});"
2d_seq = "{name}.assign({length_i}, std::vector<{type}>({length_j}));"

# 宣言と確保
[declare_and_allocate]
seq = "std::vector<{type}> {name}({length});"
2d_seq = "std::vector<std::vector<{type}>> {name}({length_i}, std::vector<{type}>({length_j}));"

# 入力
[input]
#int = "std::cin >> {name};"
int = "std::scanf(\"%lld\", &{name});"
#float = "std::cin >> {name};"
float = "std::scanf(\"%Lf\", &{name});"
str = "std::cin >> {name};"
```

例えばPythonでの設定方法は以下です。
```toml
base_indent = 1
insert_space_around_operators = true

# global変数宣言時の接頭辞
global_prefix = ""

# インデックス
[index]
i = "i"
j = "j"

# ループ
[loop]
header = "for {loop_var} in range({length}):"
footer = ""

# タイプ
[type]
int = "int"
float = "float"
str = "str"

# デフォルト値
[default]
int = "int()"
float = "float()"
str = "str()"

# 宣言
[declare]
int = ""
float = ""
str = ""
seq = ""
2d_seq = ""

# 確保
[allocate]
seq = "{name} = [{default}] * ({length})"
2d_seq = "{name} = [[{default}] * ({length_j}) for _ in {length_i}]"

# 宣言と確保
[declare_and_allocate]
seq = "{name} = [{default}] * ({length})  # type: \"List[{type}]\""
self.declare_and_allocate_2d_seq = "{name} = [[{default}] * ({length_j}) for _ in {length_i}]  # type: \"List[List[{type}]]\""

# 入力関数
[input_func]
int = "int(next(tokens))"
float = "float(next(tokens))"
str = "next(tokens)"

# 入力
[input]
int = "{name} = {input_func}"
float = "{name} = {input_func}"
str = "{name} = {input_func}"

# 宣言と入力
[declare_and_input]
int = "{name} = {input_func}  # type: int"
float = "{name} = {input_func}  # type: float"
str = "{name} = {input_func}  # type: str"

# 確保と入力
[allocate_and_input]
seq = "{name} = [{input_func} for _ in range({length})]"
2d_seq = "{name} = [[{input_func} for _ in range({length_j})] for _ in range({length_i})]"

# 宣言と確保と入力
[declare_and_allocate_and_input]
seq = "{name} = [{input_func} for _ in range({length})]  # type: \"List[{type}]\""
2d_seq = "{name} = [[{input_func} for _ in range({length_j})] for _ in range({length_i})]  # type: \"List[List[{type}]]\""

# 引数
[arg]
int = "{name}: int"
float = "{name}: float"
str = "{name}: str"
seq = "{name}: \"List[{type}]\""
2d_seq = "{name}: \"List[List[{type}]]\""

# 配列アクセス
[access]
seq = "{name}[{index}]"
2d_seq = "{name}[{index_i}][{index_j}]"
```

## テンプレートの例
`atcoder-tools gen`コマンドに対し`--template`でテンプレートソースコードを指定できます。
テンプレートエンジンの仕様については[jinja2](http://jinja.pocoo.org/docs/2.10/) の公式ドキュメントを参照してください。

テンプレートに渡される変数は以下の通りです。


- **prediction_success** 入力形式の推論に成功したとき `True`、 失敗したとき `False`が格納されている。この値が`True`のとき次の3種類の変数も存在することが保証される。
    - **input_part** input用のコード
    - **formal_arguments** 型つき引数列
    - **actual_arguments** 型なし引数列

- **mod** 問題文中に存在するmodの整数値
- **yes_str** 問題文中に存在する yes や possible などの真を表しそうな文字列値
- **no_str** 問題文中に存在する no や impossible などの偽を表しそうな文字列値

```c++
#include <bits/stdc++.h>
using namespace std;

{% if mod %}
const long long MOD = {{ mod }};
{% endif %}
{% if yes_str %}
const string YES = "{{ yes_str }}";
{% endif %}
{% if no_str %}
const string NO = "{{ no_str }}";
{% endif %}

{% if prediction_success %}
void solve({{ formal_arguments }}){

}
{% endif %}

int main(){
    {% if prediction_success %}
    {{input_part}}
    solve({{ actual_arguments }});
    {% else %}
    // Failed to predict input format
    {% endif %}
    return 0;
}
```


## Contribution

[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## Licence

[MIT](https://github.com/kyuridenamida/ToolsForAtCoder/blob/master/LICENCE)

## Author

[kyuridenamida](https://github.com/kyuridenamida) ([@kyuridenamida](https://twitter.com/kyuridenamida))
