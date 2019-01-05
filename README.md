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

以下は、コードスタイルの設定が幅4のスペースインデントで、
問題用ディレクトリ内で毎回`clang-format`を実行して、最後に`CMakeLists.txt`(空)をコンテスト用ディレクトリに生成する場合の`~/.atcodertools.toml`の例です。

```$xslt
[codestyle]
indent_type = 'space' # 'tab' or 'space'
indent_width = 4

[postprocess]
exec_on_each_problem_dir='clang-format -i ./*.cpp'
exec_on_contest_dir='touch CMakeLists.txt'
```




## Contribution
気軽にPRを送ってください。

## Licence

[MIT](https://github.com/kyuridenamida/ToolsForAtCoder/blob/master/LICENCE)

## Author

[kyuridenamida](https://github.com/kyuridenamida) ([@kyuridenamida](https://twitter.com/kyuridenamida))
