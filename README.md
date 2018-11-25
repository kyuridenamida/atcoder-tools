atcoder-tools
====

** ToolsForAtCoder changes the name to atcoder-tools on 12/03/2016 **

Convenient modules for [AtCoder](http://atcoder.jp/) users, written in Python 3.4!
This tool can analyze the input format with high accuracy (90% Accuracy for ARC or ABC).

AtCoderを解析する際に便利なモジュール群です．このツールには入力解析機能があり，ARCやABCについては高精度(90%)での入力解析を実現しています．

## Description

I develop convenient modules for AtCoder users, especially about pulling data from AtCoder sites, input format analysis or automatic code generation.

This tool provides modules related to the following things.

- Log-in, Extracting information(Ex. examples) from pulled data, Automatic submission
- Input format analysis by backtracking algorithm which works fast.
- automatic cpp's template code generation using a result of analysis.

At the time, you can generate only cpp's template code.
However you can make another language's template easily by modifying the code!

便利なモジュール群，特にAtCoderからデータを取ってきたり，入力フォーマット解析，コードの自動生成などに関するものを実装しています．

このツールは以下に関するモジュールを提供しています．
- AtCoderへのログイン，入出力例データなどの抽出，自動提出
- 枝刈り探索による高速な入力解析
- 解析結果を用いたテンプレートコードの自動生成

コード生成は現時点でcppにのみ対応していますが，cppのコード生成部分を少し弄れば他の言語にも容易に対応することができます．

## Demo
[Video demo for 'Tools For AtCoder'](https://youtu.be/Ee3EWs_xHG8)

## Requirement

- Python 3.4
- Beautiful soup 4

## Usage


If you want to use this tool as an atcoder client (beta ver), the following example will be helpful. 

クライアントとしてこのツールを使いたい人(C++ユーザー)は以下のような感じで実行すると良いです．

```
$ python3 ./AtCoderClient.py [contestid]
AtCoder username: username
AtCoder password: ***
$ cd ./workspace/[contestid]/[problem_id]/
$ {Compile something}
$ ../../../tools/tester.py
$ python tester.py
```

You can skip to input the username and password using the `--without-login` argument.

`--without-login` 引数を指定するとログインなしでデータをダウンロードできます(一般公開されているコンテストのみ)。

```
$ python3 ./AtCoderClient.py [contestid] --without-login
```

If you feel annoyed at typing password many times, you can prepare an account information file.

もしパスワードを毎回入力するのが面倒くさいならアカウント情報のファイルを作ってください。
```
$ echo "password = 'AtCoder password'; username = 'AtCoder username'" > ./AccountInformation.py # Be careful with the password management!!!
```

If you're a developer who wants to use some modules for analysis, please read the codes or please ask me anything!

開発者の方はソース読むか，気軽にkyuridenamidaに質問してください．

## Install

```
$ pip install beautifulsoup4
$ git clone https://github.com/kyuridenamida/ToolsForAtCoder.git
```

## Contribution

1. Fork it ( https://github.com/kyuridenamida/ToolsForAtCoder/fork )
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request


## Licence

[MIT](https://github.com/kyuridenamida/ToolsForAtCoder/blob/master/LICENCE)

## Author

[kyuridenamida](https://github.com/kyuridenamida) ([@kyuridenamida](https://twitter.com/kyuridenamida))

# Files

```
.
├── AccountInformation.py -- (option) Account information! This file is not on the repository! 
├── AtCoderClient.py -- A client for preparing workplace.
├── README.md 
├── tools
│   └── tester.py -- tests with samples using some executable file in your directory. You should add
│                     this directory to PATH environment variable, so you can use this everywhere.
├── templates
│   ├── cpp
│   │     ├── cpp_code_generator.py -- You can get some hint to make other templates from this file.
│   │     ├── template_failure.cpp
│   │     └── template_success.cpp
│   └── java
│          ├── java_code_generator.py 
│          ├── template_failure.java
│          └── template_success.java
├── benchmark
│   ├── overall_test.py -- does testing with all public problems on AtCoder. 
│   ├── support_list.html -- Test result(html ver)
│   └── support_list.md -- Test result(markdown ver)
├── core 
│   ├── AtCoder.py -- deals with logging-in, getting information of a contest and submitting source code.
│   ├── Calculator.py -- calculates a formula as string text with variables.
│   ├── FormatAnalyzer.py -- detects the loop structures in the format using FormatTokenizer.py's result 
│   │                        and determines what type the variables are.
│   ├── FormatPredictor.py -- gets the structured input format using FormatAnalyzer.py's result.
│   ├── FormatTokenizer.py -- converts a plain input format text into all possible tokenized formats.
│   ├── TemplateEngine.py -- generates source file with given variables.
│   └── utils.py -- Utilities
└── etc
     └── lecture.md
```
