from dataclasses import asdict
from datetime import date, timedelta

import polars as pl

from threads import Threads


def main():
    # sinceに昨日の日付を設定してThreadsのall_postsを取得する
    today = date.today()
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()

    threads = Threads()
    posts = threads.get_all_posts(since=since)

    # postsをpolarsのdataframeにする
    df_posts = pl.from_dicts([asdict(post) for post in posts])
    # df_postsを "dist/posts.jsonl" ファイルへ保存する
    df_posts.write_ndjson("dist/posts.jsonl")


if __name__ == "__main__":
    main()
