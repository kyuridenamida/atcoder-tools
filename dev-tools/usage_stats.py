#!/usr/bin/env python3
"""atcoder-tools の利用状況 (PyPI ダウンロード数・GitHub トラフィック) を Markdown で出力する。

使い方: python3 dev-tools/usage_stats.py > usage.md
標準ライブラリのみで動く。GitHub トラフィックは `gh` CLI (リポジトリの push 権限) があるときだけ出力する。
"""
import json
import subprocess
import time
import urllib.request
from collections import defaultdict

PACKAGE = "atcoder-tools"
REPO = "kyuridenamida/atcoder-tools"


def monthly(rows):
    """[{category, date: 'YYYY-MM-DD', downloads}] -> {month: {category: downloads}}"""
    res = defaultdict(lambda: defaultdict(int))
    for r in rows:
        res[r["date"][:7]][r["category"]] += r["downloads"]
    return res


def share(rows):
    """カテゴリ別の合計を多い順に [(category, downloads, 割合%)] で返す"""
    total = defaultdict(int)
    for r in rows:
        total[r["category"]] += r["downloads"]
    s = sum(total.values()) or 1
    return [(c, d, 100 * d / s) for c, d in sorted(total.items(), key=lambda x: -x[1])]


def pypistats(endpoint):
    # pypistats.org は直近180日分のみ保持し、連続アクセスは 429 になるので間隔を空ける
    time.sleep(2)
    req = urllib.request.Request(
        f"https://pypistats.org/api/packages/{PACKAGE}/{endpoint}",
        headers={"User-Agent": "atcoder-tools-usage-stats"})
    with urllib.request.urlopen(req, timeout=30) as f:
        return json.load(f)["data"]


def gh(path):
    try:
        out = subprocess.run(["gh", "api", f"repos/{REPO}{path}"],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    print(f"# {PACKAGE} 利用状況\n")
    print("## PyPI 月別ダウンロード数 (直近180日。両端の月は部分月)\n")
    print("| 月 | ミラー除く | ミラー含む |\n|---|---:|---:|")
    for month, d in sorted(monthly(pypistats("overall")).items()):
        print(f"| {month} | {d['without_mirrors']} | {d['with_mirrors']} |")

    for title, endpoint in [("Python バージョン", "python_minor"), ("OS", "system")]:
        print(f"\n## {title}別 (直近180日, ミラー除く)\n")
        print("| 区分 | DL数 | 割合 |\n|---|---:|---:|")
        for c, d, p in share(pypistats(endpoint)):
            print(f"| {'不明 (bot等)' if c == 'null' else c} | {d} | {p:.1f}% |")

    repo = gh("")
    if repo is None:
        print("\n(GitHub: `gh` CLI が使えないためスキップ)")
        return
    print("\n## GitHub\n")
    print(f"- Star: {repo['stargazers_count']} / Fork: {repo['forks_count']}")
    for name, path in [("clone", "/traffic/clones"), ("閲覧", "/traffic/views")]:
        t = gh(path)  # 直近14日分のみ。push 権限が必要
        if t:
            print(f"- 直近14日の{name}: {t['count']} 回 (ユニーク {t['uniques']})")
    refs = gh("/traffic/popular/referrers")
    if refs:
        print("- 流入元: " +
              ", ".join(f"{r['referrer']} ({r['count']})" for r in refs))


def self_check():
    rows = [{"category": "a", "date": "2026-01-01", "downloads": 1},
            {"category": "a", "date": "2026-01-31", "downloads": 2},
            {"category": "b", "date": "2026-02-01", "downloads": 1}]
    assert monthly(rows) == {"2026-01": {"a": 3}, "2026-02": {"b": 1}}
    assert share(rows) == [("a", 3, 75.0), ("b", 1, 25.0)]


if __name__ == "__main__":
    self_check()
    main()
