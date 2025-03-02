import json
import os
from dataclasses import dataclass
from pprint import pp
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()
THREADS_TOKEN = os.environ.get("THREADS_TOKEN", "")
THREADS_API_BASE = "https://graph.threads.net/v1.0"


def _call_api_get(path: str, data: list[tuple[str, str]] = []) -> dict:
    """APIにGETリクエストを送る"""
    headers = {
        "Authorization": f"Bearer {THREADS_TOKEN}",
    }

    url = f"{THREADS_API_BASE}{path}"
    if data:
        url += f"?{urlencode(data)}"

    print(url)
    req = Request(url, headers=headers)
    with urlopen(req) as res:
        body = res.read()
        return json.loads(body)


@dataclass
class ThreadPost:
    id: str
    media_product_type: str
    media_type: str
    media_url: str
    permalink: str
    owner_id: str
    username: str
    text: str
    timestamp: str
    is_quote_post: bool
    has_replies: bool
    quoted_post_id: str


class Threads:
    """Threadsの操作をするクラス
    参考:
        - https://developers.facebook.com/docs/threads/reference/user
        - https://developers.facebook.com/docs/threads/threads-media#retrieve-a-list-of-all-a-user-s-threads
    """

    id = ""
    user_name = ""
    name = ""

    def __init__(self):
        me_res = _call_api_get("/me", [("fields", "id,username,name")])
        print(me_res)
        self.id = me_res.get("id", "")
        self.user_name = me_res.get("username", "")
        self.name = me_res.get("name", "")

    def get_threads(
        self,
        limit: int = 100,
        since: str = None,
        until: str = None,
        before: str = None,
        after: str = None,
    ) -> tuple[list[ThreadPost], str, str]:
        """自身のThreads投稿のリストを取得する
        Args:
            limit: 一度に取得する件数。最大100件
            since: いつからのデータを取得するか。例： "2025-02-11"
            until: いつまでのデータを取得するか。例： "2025-02-12"
            before: 検索結果の１つ前を取得する場合に指定。
            after: 検索結果の１つ後を取得する場合に指定。
        Returns:
            - 投稿のリスト
            - before
            - after
        """
        fields = [
            "id",
            "media_product_type",
            "media_type",
            "media_url",
            "permalink",
            "owner",
            "username",
            "text",
            "timestamp",
            "is_quote_post",
            "has_replies",
            "quoted_post",
        ]
        params = [
            ("limit", limit),
            ("fields", ",".join(fields)),
        ]
        if since:
            params.append(("since", since))
        if until:
            params.append(("until", until))
        if before:
            params.append(("before", before))
        if after:
            params.append(("after", after))

        res = _call_api_get(
            f"/{self.id}/threads",
            params,
        )
        pp(res)

        # before, afterを取得
        cursors = res.get("paging", {}).get("cursors", {})
        cursor_before = cursors.get("before", "")
        cursor_after = cursors.get("after", "")

        posts = res.get("data", [])
        threads_posts = [
            ThreadPost(
                id=p.get("id", ""),
                media_product_type=p.get("media_product_type", ""),
                media_type=p.get("media_type", ""),
                media_url=p.get("media_url", ""),
                permalink=p.get("permalink", ""),
                owner_id=p.get("owner", {}).get("id", ""),
                username=p.get("username", ""),
                text=p.get("text", ""),
                timestamp=p.get("timestamp", ""),
                is_quote_post=p.get("is_quote_post", False),
                has_replies=p.get("has_replies", False),
                quoted_post_id=p.get("quoted_post", {}).get("id", ""),
            )
            for p in posts
        ]
        return (threads_posts, cursor_before, cursor_after)
