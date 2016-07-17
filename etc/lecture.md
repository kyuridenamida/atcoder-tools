## Python3+bs4で AtCoderの便利スクリプトを作る
Python3とbs4(beautifulsoup4)でAtCoderの便利スクリプトを作る．

対象読者はWebスクレイピングしたいけど，ブラウザ以外からのログインさえできる気がしないって人です．Pythonよくしらない人向けに書いたつもりでしたが，僕もPython初心者で教え方が全くわからないのでちょっと厳しいかも．

かなり手を抜いているのでコメントか直接何かしらの手段で質問してくれたら答えたいと思います．すみません．

### bs4 をインストールしよう
bs4は何をしてくれるやつかっていうと，htmlとかxmlのタグをパースしてくれるというか，必要な情報抜き出してくれるやつです．
正規表現とかガリガリ駆使しながらタグ抜き出す作業するのは楽しいけどめんどいいので，そういった面倒臭さから僕達を遠ざけてくれます．
嬉しい!

```
pip install beautifulsoup4
```
でOK．pipがない人はインストールしといてください．

### AtCoderにPythonからログインしよう
AtCoderにPythonからログインします．

#### ログインするためにはどういう手順を踏めばいい?
自分のアカウントでログインしたクッキーを維持しながらサイト内をWebスクレイピング(ウェブサイトから情報を抽出すること)しないといけません．

これはPython3に標準搭載されているurllibというインターネット上のリソースを取得するためのパッケージを使うと簡単に実現できます．

ログインはどのように行われるかというと，AtCoder(を含むいろいろなサイト)はPOSTリクエストという形式でログインに必要な入力データを持ってあるURLにリクエストすると，ログイン処理を行ってくれるように出来ています．

AtCoderのログインフォーム(https://arc001.contest.atcoder.jp/login)
を見ると，以下のようになっています．

* ユーザー名の部分
```
<input type="text" id="name" class="input-xlarge" name="name" value="" autocomplete="off">
```

* パスワードの部分
```
<input type="password" id="name" class="input-xlarge" name="password" value="">
```

name部分が重要に注目してください．"name"と"password"になっていますね．
これに関するデータをPOST形式で渡すときの要素名になります．

#### 実際にログインしてみる

さっそくAtCoderにログインしてみましょう．

ディクショナリをPOSTデータの実質の形式(password=パスワード&name=ユーザー名)にしてくれる関数urllib.parse.urlencode()があるので，それを使います．

```py
username,password = 'ユーザー名','パスワード'
postdata = {
    'name': username,
    'password': password
}
encoded_postdata = urllib.parse.urlencode(postdata).encode('utf-8')
req = opener.open("https://arc001.contest.atcoder.jp/login",encoded_postdata)

print(req.read().decode('utf-8')) # req.read()だけだとバイナリで表示されてよくわからないのでutf8の文字列に変換
```
ログインに成功するとトップページに飛ぶので，
表示されたソースに「パスワードを忘れた方はこちら」とかが無ければログインに成功しています．
おめでとうございます．

参考にさせて頂いたサイト様: http://stackoverflow.com/questions/5010915/how-do-i-clear-the-cookies-in-urllib-request-python3

### AtCoderから情報を取得してこよう

#### 問題番号とそれに対応するリストを取得してみる
ひとたび/loginにアクセスしてログインに成功したら，openerにクッキーの情報が紐付いてくれているので，あとは好き放題リクエストしまくりです．

では，問題番号とそれに対応するURLのリストを取得してみましょう．
課題ページ(http://arc001.contest.atcoder.jp/assignments )のソースを見て，問題へのリンクがあるところを抜き出すと，以下のようになっています．
```
<td class="center"><a class="linkwrapper" href="/tasks/arc001_1">A</a></td>
<td><a class="linkwrapper" href="/tasks/arc001_1">センター採点</a></td>
```
どうやら運の良いことに問題ページのURLにリンクされている⇔classがlinkwrapperであるタグで囲まれているということが分かりますね．

soupのオブジェクトを作って，select関数で.linkwrapperクラスのタグを全列挙してみましょう．

以下のコードにドットがついているのはcssのclassだからだと思います．
```py
req = opener.open("http://arc001.contest.atcoder.jp/assignments")
soup = BeautifulSoup(req,"html.parser")
for tag in soup.select('.linkwrapper'):
  print(tag)
```

実行結果は以下のようになると思います．
実際にはtagは文字列型ではなくいろいろ操作ができるオブジェクトですが，あくまでprintした時の挙動はタグそのものを出力します．
```
<a class="linkwrapper" href="/tasks/arc001_1">A</a>
<a class="linkwrapper" href="/tasks/arc001_1">センター採点</a>
<a class="linkwrapper" href="/tasks/arc001_2">B</a>
<a class="linkwrapper" href="/tasks/arc001_2">リモコン</a>
<a class="linkwrapper" href="/tasks/arc001_3">C</a>
<a class="linkwrapper" href="/tasks/arc001_3">パズルのお手伝い</a>
<a class="linkwrapper" href="/tasks/arc001_4">D</a>
<a class="linkwrapper" href="/tasks/arc001_4">レースゲーム</a>
```

1つの問題につき2つリンクがあるので，これはお好みですが0,2,4,...番目だけ取り出せばいい感じになると思います．どうせこのへん賢くやっても仕様変更されたらおしまいなので，その時点で動いてればいいんじゃないでしょうか．

せっかくなので問題番号とそれに紐付いたURLというタプルのリストを作ってみましょう．
PythonはすごいのでリストXに対してX[0::2]とすると2個飛ばしでリストを抜き出してくれます．
こんなかんじになります．
```py
X = []
for tag in soup.select('.linkwrapper')[0::2]:
	problemid = tag.text
	url = "http://arc001.contest.atcoder.jp"+tag.get("href")
  	X.append((problemid,url))
print(X)
```
ここで，tagのメンバとかメソッドでtextとかget("href")とかありますが，これはそれぞれタグの囲まれている中身やタグの属性を取得してくれる便利なやつです．

出力結果は以下の通りです．

```
[('A', 'http://arc001.contest.atcoder.jp/tasks/arc001_1'), ('B', 'http://arc001.contest.atcoder.jp/tasks/arc001_2'), ('C', 'http://arc001.contest.atcoder.jp/tasks/arc001_3'), ('D', 'http://arc001.contest.atcoder.jp/tasks/arc001_4')]
```

ところで，リスト内包表記という記法を使ってタプルのリストを作るソースが以下のようになります．
こういうワンライナーな使い方をすると可読性が低い気もしますが書きやすいです．
```py
print([(tag.text,"http://arc001.contest.atcoder.jp"+tag.get("href")) for tag in soup.select('.linkwrapper')[0::2]])
```

#### 問題文からサンプルを抜き出そう
あとはやることは同じです．
ソースがどういう構造になってるか眺めながら，特徴になってきそうな部分を取り出してくるだけです．
どうやら入出力の枠はpreタグで表現されているみたいです．これを全て取得すれば常勝では!?

しかし，気をつけることがあります．AtCoderの問題文は作る人によってhtmlのフォーマットが微妙に違うっぽいです．
具体的な例としては，preタグを入力形式・サンプル入出力以外にも使っている作問者がいるということが挙げられます．

ちなみにpreタグについている属性も人によってまちまちなので，あまりそこを情報として使うとよくないかも．

ただまあ，大体はお行儀の良い感じになっているはずなので，取得してみてバグったら修正を繰り返してればなんとかなるはずです．

#### ARC001で試してみる
ARC001のA問題(http://arc001.contest.atcoder.jp/tasks/arc001_1 )に対して，preタグでフィルタをかけてみましょう．

```py
req = opener.open("http://arc001.contest.atcoder.jp/tasks/arc001_1")
soup = BeautifulSoup(req,"html.parser")
for tag in soup.select('pre'):
  print(tag)
```

```
<pre>
<var>N</var>
<var>c_1c_2c_3…c_N</var>
</pre>
<pre class="prettyprint linenums">
9
131142143
</pre>
<pre class="prettyprint linenums">
4 1
</pre>
<pre class="prettyprint linenums">
20
12341234123412341234
</pre>
<pre class="prettyprint linenums">
5 5
</pre>
<pre class="prettyprint linenums">
4
1111
</pre>
<pre class="prettyprint linenums">
4 0
</pre>
```

かなりいい感じに取れましたが，入力の項が混ざっています．これを取り除くために，一例として以下の方針が考えられます．

1. prettyprintもしくはlinenumsクラスをselectに指定する

2. 1つ目の取得結果を問答無用で取り除く

ARC001〜ARC004の範囲ならどちらの方針でも正しく動きそうです．
必要・十分条件とどれくらいのコンテストに対して成り立ちそうかみたいなのを強く意識すると正しい選択ができるかもしれませんが，これといった正解はないです．アドホックです．

まあとりあえずそのへんどう処理するかはおいおい考えるとして，
とりあえず入力と出力を切り分けてみます．**2.の方針のほうが多分多くのケースを網羅できるんですが**，今回は1.の方針でやってみましょう．

```py
opener = opener.open("http://arc001.contest.atcoder.jp/tasks/arc001_1")
soup = BeautifulSoup(req,"html.parser")
tags = soup.select('.prettyprint')
input_tags = tags[0::2]
output_tags = tags[1::2]
# len(input_tags) == len(output_tags) は勝手に仮定
for i in range(len(input_tags)):
  print("---- sample %d ----" % i) # こういう記法です
  print(input_tags[i].text.strip()) # strip()は前後の改行空白消してくれるやつです
  print("--")
  print(output_tags[i].text.strip())
  print()

```

出力結果は以下の通りになります．
```
---- sample 0 ----
9
131142143
--
4 1

---- sample 1 ----
20
12341234123412341234
--
5 5

---- sample 2 ----
4
1111
--
4 0

```

概ねこんな感じになりました．
いい感じですね．あとはこのテキストをファイルに保存したりしたら自動ダウンローダーは完成です．おめでとうございます．

ところで，前後の改行空白を消すためにstrip()を使っていますが，不具合の元になる可能性はあります．が，そんな入力作るwriterいないと思いますし，サンプルに関してはミスって無駄に改行がある回とかがある可能性もあるのでstrip()する方針は間違ってなさそうです．

### おわりに
いかがでしたでしょうか．
実はダウンローダーツールを作っていて，そのついでに並行でこの記事を書いてみました．
自分が扱ってるコードとここに書いたコードはいろいろ違うので，もしなんかこの部分動かないよ!ってのがあったらコメントください．

bs4についてもっと知りたい人は以下の記事が参考になると思います．僕もこれを見ました．ありがとうございます．
http://qiita.com/itkr/items/513318a9b5b92bd56185
