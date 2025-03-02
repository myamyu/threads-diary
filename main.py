import os
import sys
from dataclasses import asdict
from datetime import date, timedelta

import polars as pl

from threads import Threads

thread_post_data_schema = {
    "id": pl.Utf8,
    "media_product_type": pl.Utf8,
    "media_type": pl.Utf8,
    "media_url": pl.Utf8,
    "permalink": pl.Utf8,
    "owner_id": pl.Utf8,
    "username": pl.Utf8,
    "text": pl.Utf8,
    "timestamp": pl.Utf8,
    "is_quote_post": pl.Boolean,
    "has_replies": pl.Boolean,
    "quoted_post_id": pl.Utf8,
    "reposted_post_id": pl.Utf8,
    "root_post_id": pl.Utf8,
    "replied_to_id": pl.Utf8,
}

thread_post_schema = pl.Schema(
    {
        **thread_post_data_schema,
        **{
            "quoted_post": pl.Struct(thread_post_data_schema),
            "reposted_post": pl.Struct(thread_post_data_schema),
            "root_post": pl.Struct(thread_post_data_schema),
            "replied_to": pl.Struct(thread_post_data_schema),
        },
    }
)


def _save_threads_posts(since: str, until: str = None):
    """threadsの投稿を保存する
    Args:
        since: いつからの投稿を保存するか
        until: いつまでの投稿を保存するか
    """
    threads = Threads()
    posts = threads.get_all_posts(since=since, until=until)
    df_posts = pl.from_dicts(
        [asdict(post) for post in posts], schema=thread_post_schema
    )

    # distディレクトリがなければ作成する
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # timestampの年ごとにdataframeを分けてファイルに保存
    df_posts = df_posts.with_columns(
        pl.col("timestamp").str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%S%Z").alias("date")
    ).with_columns(pl.col("date").dt.year().alias("year"))

    for year in df_posts["year"].unique():
        df_year = df_posts.filter(pl.col("year") == year)
        # df_yearのdateとyearカラムを除外する
        df_year = df_year.drop(["date", "year"])

        # すでにファイルがある場合はデータを読み込んで重複を削除して保存
        file_path = f"dist/posts_{year}.jsonl"
        if os.path.exists(file_path):
            df_old = pl.read_ndjson(file_path, schema=thread_post_schema)
            df_year = pl.concat([df_old, df_year]).unique(subset=["id"])

        # df_yearを "dist/posts_{year}.jsonl" ファイルへ保存する
        df_year.write_ndjson(file_path)


def main():
    today = date.today()
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()

    # sinceとuntilのコマンドライン引数があればそれを採用する
    if len(sys.argv) > 1:
        since = sys.argv[1]
        if since == "all":
            since = ""

    until = ""
    if len(sys.argv) > 2:
        until = sys.argv[2]

    _save_threads_posts(since=since, until=until)


if __name__ == "__main__":
    main()
