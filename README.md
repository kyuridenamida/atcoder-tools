[![Build Status](https://travis-ci.org/kyuridenamida/atcoder-tools.svg?branch=master)](https://travis-ci.org/kyuridenamida/atcoder-tools)
[![codecov](https://codecov.io/gh/kyuridenamida/atcoder-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/kyuridenamida/atcoder-tools)
[![PyPI](https://img.shields.io/pypi/v/atcoder-tools.svg)](https://pypi.python.org/pypi/atcoder-tools)

atcoder-tools
====
Python 3.5 で動作する [AtCoder](http://atcoder.jp/) からサンプル入力をダウンロードしたりする際に便利なツールです。

このツールには次のような機能があります。
- AtCoderへのログイン，入出力例データなどの抽出
- 枝刈り探索による高精度・高速な入力解析 (ARC、ABC、AGCについては約9割ほど)
- 解析結果を用いたテンプレートコードの自動生成(C++, Java)
    - 他言語対応のためのコントリビューション(≒中間形式からコードに変換する部分のPR)を募集中です!

## How to install
`pip3 install atcoder-tools`

## Demo
<a href="https://asciinema.org/a/JG18AGOE2Vw7Tsa3QTM7Y2XX5">
    <img src="https://asciinema.org/a/JG18AGOE2Vw7Tsa3QTM7Y2XX5.svg" width=70%>
</a>

## Usage


*重要: かつてパスワード入力なしでログインを実現するために`AccountInformation.py`にログイン情報を書き込むことを要求していましたが、セキュリティリスクが高すぎるため、セッション情報のみを保持する方針に切り替えました。
今後はできるだけ保持されているセッション情報を利用してAtCoderにアクセスし、必要に応じて再入力を要求します。
過去のユーザーの皆様には`AccountInformation.py`を削除して頂くようお願い申し上げます。*


- `atcoder-tools gen {contest_id}` コンテスト環境を用意するコマンド
- `atcoder-tools test` カレント・ディレクトリ上に実行ファイルと入出力(in_\*.txt, out_\*.txt)がある状態で実行するとローカルテストを行う
- `atcoder-tools submit` カレント・ディレクトリ上で実行すると対応する問題がサンプルに通る場合ソースコードを提出します。既にAtCoder上にその問題に対する提出がある場合、`-u`を指定しないと提出できないようになっています。

`atcoder-tools gen --help`で`atcoder-tools gen`の引数の詳細について確認することができます。

例: 
```
$ atcoder-tools gen agc001
$ cd ~/atcoder-workspace/agc001/A
$ g++ main.cpp
$ atcoder-tools test
```

`--without-login` 引数を指定するとログインなしでデータをダウンロードできます(一般公開されているコンテストのみ)。

```
$ atcoder-tool gen  [contest_id] --without-login
```

### gen の詳細
```$xslt
usage: atcoder-tools gen [-h] [--without-login]
                                                        [--workspace WORKSPACE]
                                                        [--lang LANG]
                                                        [--template TEMPLATE]
                                                        [--replacement REPLACEMENT]
                                                        [--parallel]
                                                        [--save-no-session-cache]
                                                        [--config CONFIG]
                                                        contest_id

positional arguments:
  contest_id            Contest ID (e.g. arc001)

optional arguments:
  -h, --help            show this help message and exit
  --without-login       Download data without login
  --workspace WORKSPACE
                        Path to workspace's root directory. This script will create files in {WORKSPACE}/{contest_name}/{alphabet}/ e.g. ./your-workspace/arc001/A/
                        [Default] ${HOME}/atcoder-workspace
  --lang LANG           Programming language of your template code, cpp or java.
                        [Default] cpp
  --template TEMPLATE   File path to your template code
                        [Default (C++)] /atcodertools/tools/templates/cpp/template_success.cpp
                        [Default (Java)] /atcodertools/tools/templates/java/template_success.java
  --replacement REPLACEMENT
                        File path to your config file
                        [Default (C++)] /atcodertools/tools/templates/cpp/template_failure.cpp
                        [Default (Java)] /atcodertools/tools/templates/java/template_failure.java
  --parallel            Prepare problem directories asynchronously using multi processors.
  --save-no-session-cache
                        Save no session cache to avoid security risk
  --config CONFIG       File path to your config file
                        [Default (Primary)] ${HOME}/.atcodertools.toml
                        [Default (Secondary)] /atcodertools/tools/atcodertools-default.toml

```

### test の詳細

```$xslt
usage: atcoder-tools test [-h] [--exec EXEC]
                                                         [--num NUM]
                                                         [--dir DIR]
                                                         [--timeout TIMEOUT]
                                                         [--knock-out]

optional arguments:
  -h, --help            show this help message and exit
  --exec EXEC, -e EXEC  File path to the execution target. [Default] Automatically detected exec file
  --num NUM, -n NUM     The case number to test (1-origin). All cases are tested if not specified.
  --dir DIR, -d DIR     Target directory to test. [Default] Current directory
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout for each test cases (sec) [Default] 1
  --knock-out, -k       Stop execution immediately after any example's failure [Default] False

```


### submit の詳細

```
usage: atcoder-tools submit [-h] [--exec EXEC]
                                                           [--dir DIR]
                                                           [--timeout TIMEOUT]
                                                           [--code CODE]
                                                           [--force]
                                                           [--save-no-session-cache]
                                                           [--unlock-safety]

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

```


## 設定ファイルの例
`~/.atcodertools.toml`に以下の設定を保存すると、コードスタイルや、コード生成後に実行するコマンドを指定できます。

以下は、次の挙動を期待する場合の`~/.atcodertools.toml`の例です。

- コードスタイルの設定が幅4のスペースインデントである
- コード生成テンプレートとして`~/my_template.cpp`を使う
- 問題用ディレクトリ内で毎回`clang-format`を実行して、最後に`CMakeLists.txt`(空)をコンテスト用ディレクトリに生成する
- カスタムコードジェネレーター `custom_code_generator.py`を指定す

```$xslt
[codestyle]
indent_type = 'space' # 'tab' or 'space'
indent_width = 4
template_file='~/my_template.cpp'
[postprocess]
exec_on_each_problem_dir='clang-format -i ./*.cpp'
exec_on_contest_dir='touch CMakeLists.txt'
code_generator_file="~/custom_code_generator.py"
```

### カスタムコードジェネレーター
[標準のC++コードジェネレーター](https://github.com/kyuridenamida/atcoder-tools/blob/master/atcodertools/codegen/code_generators/cpp.py)に倣って、
`(CogeGenArgs) -> str(ソースコード)`が型であるような`main`関数を定義した.pyファイルを`code_generator_file`で指定すると、コード生成時にカスタムコードジェネレーターを利用できます。
 
## テンプレートの例
`atcoder-tools gen`コマンドに対し`--template`, `--replacement` でそれぞれ入力形式の推論に成功したときのテンプレート、生成に失敗したときに代わりに生成するソースコードを指定できます。テンプレートエンジンの仕様については[jinja2](http://jinja.pocoo.org/docs/2.10/) の公式ドキュメントを参照してください。テンプレートに渡される変数は以下の通りです。

- **input_part** input用のコード
- **formal_arguments** 型つき引数列
- **actual_arguments** 型なし引数列

- **mod** 問題文中に存在するmodの値
- **yes_str** 問題文中に存在する yes や possible などの真を表しそうな値
- **no_str** 問題文中に存在する no や impossible などの偽を表しそうな値

```
#include <bits/stdc++.h>
using namespace std;

{% if mod %}const int mod = {{ mod }};{% endif %}
{% if yes_str %}const string YES = "{{ yes_str }}";{% endif %}
{% if no_str %}const string NO = "{{ no_str }}";{% endif %}

void solve({{formal_arguments}}){

}

int main(){
    {{input_part}}
    solve({{actual_arguments}});
    return 0;
}
```


## Contribution
気軽にPRを送ってください。

## Licence

[MIT](https://github.com/kyuridenamida/ToolsForAtCoder/blob/master/LICENCE)

## Author

[kyuridenamida](https://github.com/kyuridenamida) ([@kyuridenamida](https://twitter.com/kyuridenamida))
