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

## History

|  日付  |  ログ  |
| ---- | ---- |
|  2018-12-25  | 長らく触っておらずメンテナンスが困難になってしまったので、下位互換性のない大規模コードベース変更を実施した。(すみません!) |
|  2018-12-03  | ToolsForAtCoder は atcoder-tools に名前を変更した。 |
|  2016-04-01  | 最初のバージョンをリリースした。 |

## How to install
`pip3 install atcoder-tools`

## Demo
※最初期のデモなので今とインターフェイスが異なります

[Video demo for 'Tools For AtCoder'](https://youtu.be/Ee3EWs_xHG8)


## Usage


*重要: かつてログイン情報を保持するために`AccountInformation.py`に書き込むことを要求していましたが、セキュリティリスクが高すぎるため、セッション情報のみを保持する方針に切り替えました。
過去のユーザーの方はそのファイルを削除することを推奨します。*


- `atcoder-tools gen {contest_id}` コンテスト環境を用意するコマンド
- `atcoder-tools test` カレント・ディレクトリ上に実行ファイルと入出力(in_\*.txt, out_\*.txt)がある状態で実行するとローカルテストを行う

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


## Contribution
気軽にPRを送ってください。

## Licence

[MIT](https://github.com/kyuridenamida/ToolsForAtCoder/blob/master/LICENCE)

## Author

[kyuridenamida](https://github.com/kyuridenamida) ([@kyuridenamida](https://twitter.com/kyuridenamida))
