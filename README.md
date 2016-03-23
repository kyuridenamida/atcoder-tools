# え，何これは
AtCoderの入力形式とかをがんばって解析するツールなどなどです．

# 動作環境
Python3とbeautifulsoup4があれば動くと思います．Python2では動きません．

bs4は，

```
pip install beautifulsoup4
```

で入ります．多分

# ファイル構成

- (gitignore)AccountInformation.py : passwordという変数とusernameという変数が格納されています．
- AtCoder.py : AtCoderからデータをダウンロードしてくるコードです
- Calculator.py : 文字列に関する簡易計算機です．構文木を構築して，それを評価したりできます．四則演算や括弧，変数に対応しています．
- FormatAnalyzer.py : FormatTokenizerでtokenizeされたものを与えると，入力の繰り返し部分などを検出して木構造型のデータ構造を構築します．
- FormatTokenizer.py : 入力に現れる変数列のstring列を与えて，変数名/添字に分解してくれるプログラムです．
- experiment.py : これを実行してみると全コンテストに対してデータの取得を試みて，成功した比率が表示されます．experimentalなソースなので汚いです．
- lecture.md : 開発と並行してAtCoderを用いたWebスクレイピング入門を書いたので良かったら読んでください
- sample_downloader.py : サンプルダウンロードするスクリプトです．
- utils.py : 汎用的に使いそうな関数とかを定義しています
