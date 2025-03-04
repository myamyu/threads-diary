import os

import polars as pl

from schema import thread_post_schema


def _load_threads_posts() -> pl.DataFrame:
    """dist/posts内のjsonlファイルをすべて読みこんでpolarsのdataframeにする

    Returns:
        全postsのdataframe
    """

    data_dir = "dist/posts"
    files = [f for f in os.listdir(data_dir) if f.endswith(".jsonl")]
    df_posts = pl.DataFrame(schema=thread_post_schema)
    for file in files:
        file_path = f"{data_dir}/{file}"
        df_posts = pl.concat(
            [df_posts, pl.read_ndjson(file_path, schema=thread_post_schema)]
        )
    return df_posts


def _make_page_data(df_posts: pl.DataFrame) -> dict:
    """postsの情報を各ページのデータに仕分ける
    Args:
        df_posts: postsのdataframe
    Returns:
        各ページのデータ
    """
    page_data = {
        "top": None,
        "monthly": {},
        "month_every_year": {},
        "tags": {},
    }

    # 使いやすいようにカラムを追加
    df_posts = (
        df_posts.with_columns(
            pl.col("timestamp")
            .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%Z")
            .dt.convert_time_zone("Asia/Tokyo")
            .alias("date")
        )
        .with_columns(pl.col("date").dt.strftime("%m").alias("month"))
        .with_columns(pl.col("date").dt.strftime("%Y-%m").alias("year_month"))
    )

    # TODO タグデータを作成する

    # topのデータは最新の20件を設定する
    page_data["top"] = df_posts.sort("timestamp", descending=True).head(20)

    # 年月ごとのデータを取得する
    for year_month in df_posts["year_month"].unique():
        page_data["monthly"][year_month] = df_posts.filter(
            pl.col("year_month") == year_month
        )

    # 月ごとのデータを取得する
    for month in df_posts["month"].unique():
        page_data["month_every_year"][month] = df_posts.filter(pl.col("month") == month)

    return page_data


def _output_pages(page_data: dict):
    """ページを出力する"""
    output_dir = "dist/pages"
    os.makedirs(output_dir, exist_ok=True)

    # top


def main():
    print("postsを読み込み中...")
    df_posts = _load_threads_posts()
    print(f"postsの件数: {len(df_posts)} 件")
    print("ページデータを生成中...")
    page_data = _make_page_data(df_posts)
    print("ページデータ作成完了")
    print("ページを出力中...")
    _output_pages(page_data)
    print("ページ出力完了")


if __name__ == "__main__":
    main()
