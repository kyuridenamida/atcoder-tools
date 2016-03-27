ToolsForAtCoder
====

Convenient modules written in Python 3.4 for [AtCoder](http://atcoder.jp/) users!
This tool can analyze the input format with high accuracy (90% Accuracy for ARC or ABC).

AtCoderを解析する際に便利なモジュール群です．このツールには入力解析機能があり，ARCやABCについては高精度(90%)での入力解析を実現しています．

## Description

I develop convenient modules for AtCoder users, especially about pulling data from AtCoder sites, input format analysis or automatic code generation.

This tool provide modules related the following thing:

- Log-in, Extracting pulled data(Ex. examples), Automatic submission
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
<object width="425" height="350">
  <param name="movie" value="http://www.youtube.com/user/wwwLoveWatercom?v=Ee3EWs_xHG8" />
  <param name="wmode" value="transparent" />
  <embed src="http://www.youtube.com/user/wwwLoveWatercom?v=Ee3EWs_xHG8"
         type="application/x-shockwave-flash"
         wmode="transparent" width="425" height="350" />
</object>

## Requirement

- Python 3.4
- Beautiful soup 4

## Usage


If you want to use this tool as an atcoder client (beta ver), the following example will be helpful. 

クライアントとしてこのツールを使いたい人(C++ユーザー)は以下のような感じで実行すると良いです．

```
$ echo "password = 'atcoder password'; username = 'atcoder username'" > ./AccountInformation.py # Be careful with the password management!!!
$ python3 ./AtCoderClient.py [contestid]
$ cd ./workspace/[contestid]/[problem_id]/
$ # create excetuable program
$ python3 test.py
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
├── AccountInformation.py -- Account information! This file is not on the repository!
├── AtCoderClient.py -- A beta client for cpp users.
├── CppCodeGenerator.py -- A beta module too. You can apply this code to other lang.
├── README.md 
├── benchmark
│   ├── overall_test.py -- does testing with all public problems on AtCoder. 
│   ├── support_list.html -- Test result(html ver)
│   └── support_list.md -- Test result(markdown ver)
├── core 
│   ├── AtCoder.py -- deals with login, getting information of a contest.
│   ├── Calculator.py -- calculates a formula as string text with variables.
│   ├── FormatAnalyzer.py -- detects the loop structures in the format using FormatTokenizer.py's result 
│   │                        and determine what type the variables are.
│   ├── FormatPredictor.py -- gets the structured input format using FormatAnalyzer.py's result.
│   ├── FormatTokenizer.py -- convert plain input format text into candidate tokenized formats.
│   └── utils.py -- Utilities
└── etc
    └── lecture.md
```
