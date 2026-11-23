# AGENTS.md

AI エージェント（と人）がこのリポジトリで作業するときの前提です。開発フロー全体は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 最初に知っておくこと

- **開発ブランチは `stable`** です。`master` は 2020 年で止まっており使いません。ブランチを切るのも PR を出すのも `stable` に対して行います。
- AtCoder の問題を取得し、入力形式を予測して各言語のコードを生成する CLI（`atcoder-tools gen / test / submit / codegen ...`）です。本体は `atcodertools/`、テストは `tests/` にあります。

## 変更したら必ず通すもの

```bash
poetry install
poetry run nosetests tests --exe -v
poetry run flake8 --ignore=E501,W503,W605 --exclude=atcodertools/tools/templates/,tests/resources/test_codegen/ atcodertools tests
poetry run autopep8 -r . --exclude 'default_template.py,test_codegen' --diff   # 差分が出ないこと
```

CI（`.github/workflows/tests.yml` `stylecheck.yml`）も同じコマンドを実行します。

テストは既定でネットワークもコンパイラも使わず、2 分ほどで終わります。次の 2 種類は環境変数を付けたときだけ実行され、CI では両方とも実行されます。

| 環境変数 | 実行されるテスト | 必要なもの |
|:---|:---|:---|
| `ATCODERTOOLS_TEST_NETWORK=1` | `@requires_network` を付けたテスト | atcoder.jp と PyPI への接続 |
| `ATCODERTOOLS_TEST_COMPILERS=1` | `@requires_compilers` を付けたテスト | 対応する全言語のコンパイラ（`tests.yml` 参照） |

手元でスキップされたテストは CI が確認します。手元の結果だけで「全部通った」とは言えない点に注意してください。

## ルール

1. **下位互換性を壊さない。** 過去の設定ファイル（`~/.atcodertools.toml`）と過去のコマンド・オプションが動き続けること。生成済みの `metadata.json` が読めること。難しい場合は実装前に issue で相談する。
2. **テストをネットワークに依存させない。** テスト中はソケット接続が失敗するようにしてあります（`tests/__init__.py`）。通信する処理はモックするか、実サイトでしか確認できないものに限って `@requires_network` を付けます。
3. **変更範囲を広げない。** 独立した変更は別の PR にします。触っていないコードの整形や一括リネームはしません（開いている他の PR と衝突します）。
4. **バグ修正には、修正前のコードで失敗するテストを付ける。** 新機能にもテストを書き、オプションや設定を増やしたら `README.md` を更新します。
5. **生成コードの期待値を機械的に書き換えない。** `tests/resources/**` の期待値が変わるのは、利用者が受け取る生成コードが変わるということです。意図した変化かを確認してから更新します。

## 知っておくと迷わない点

- `tests/resources/**/*.py` はテスト対象として実行されるプログラムで、テストではありません。
- 入力形式予測の全体テスト（`tests/test_fmtprediction.py`）は `tests/resources/common/test_data.tar.gz` の約 7,700 問を期待値と突き合わせます。予測ロジックを変えるとここが動きます。
- `AtCoderClient` はシングルトンです。モックするテストは `tests/test_atcoder_client_mock.py` のやり方に合わせてください。
- `webapp/` は解析結果を公開する別系統のサイトで、Python のテストや CI の対象外です。
- リリース（バージョン更新・タグ・PyPI 公開）は GitHub Actions が行います。PR でバージョン番号や `CHANGELOG.md` を書き換えないでください。
