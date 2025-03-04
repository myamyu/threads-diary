import polars as pl

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
