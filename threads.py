import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from pprint import pformat
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()
THREADS_TOKEN = os.environ.get("THREADS_TOKEN", "")
THREADS_API_BASE = "https://graph.threads.net/v1.0"

_target_fields = [
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
    "reposted_post",
    "root_post",
    "replied_to",
]


@dataclass
class ThreadPostData:
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
    reposted_post_id: str
    root_post_id: str
    replied_to_id: str


@dataclass
class ThreadPost(ThreadPostData):
    quoted_post: ThreadPostData = None
    reposted_post: ThreadPostData = None
    root_post: ThreadPostData = None
    replied_to: ThreadPostData = None


def _thread_data_to_dataclass(p: dict) -> ThreadPost:
    return ThreadPost(
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
        reposted_post_id=p.get("reposted_post", {}).get("id", ""),
        root_post_id=p.get("root_post", {}).get("id", ""),
        replied_to_id=p.get("replied_to", {}).get("id", ""),
    )


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


class Threads:
    """Threadsの操作をするクラス
    参考:
        - https://developers.facebook.com/docs/threads/reference/user
        - https://developers.facebook.com/docs/threads/threads-media#retrieve-a-list-of-all-a-user-s-threads
    """

    id = ""
    user_name = ""
    name = ""
    profile_img = ""
    biography = ""

    def __str__(self):
        return f"<Threads> {pformat(self.__dict__)}"

    def __repr__(self):
        return self.__str__()

    def __init__(self):
        me_res = _call_api_get(
            "/me",
            [
                (
                    "fields",
                    ",".join(
                        [
                            "id",
                            "username",
                            "name",
                            "threads_profile_picture_url",
                            "threads_biography",
                        ]
                    ),
                )
            ],
        )
        self.id = me_res.get("id", "")
        self.user_name = me_res.get("username", "")
        self.name = me_res.get("name", "")
        self.profile_img = me_res.get("threads_profile_picture_url", "")
        self.biography = me_res.get("threads_biography", "")

    def _get_list_data(
        self,
        data_name: str,
        limit: int = 100,
        since: str = None,
        until: str = None,
        before: str = None,
        after: str = None,
    ) -> tuple[list[ThreadPost], str, str]:
        params = [
            ("limit", limit),
            ("fields", ",".join(_target_fields)),
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
            f"/me/{data_name}",
            params,
        )

        # before, afterを取得
        cursors = res.get("paging", {}).get("cursors", {})
        cursor_before = cursors.get("before", "")
        cursor_after = cursors.get("after", "")

        posts = res.get("data", [])
        threads_posts = [_thread_data_to_dataclass(p) for p in posts]

        # quoted, repost, reply, rootのデータを取得
        target_ids = set()
        for p in threads_posts:
            if p.quoted_post_id:
                target_ids.add(p.quoted_post_id)
            if p.reposted_post_id:
                target_ids.add(p.reposted_post_id)
            if p.root_post_id:
                target_ids.add(p.root_post_id)
            if p.replied_to_id:
                target_ids.add(p.replied_to_id)

        # 取得したIDのデータを取得
        with ThreadPoolExecutor() as exector:
            futures = {exector.submit(self.get_post, id): id for id in target_ids}
            for future in futures:
                post = future.result()
                for p in threads_posts:
                    if p.quoted_post_id == post.id:
                        p.quoted_post = post
                    if p.reposted_post_id == post.id:
                        p.reposted_post = post
                    if p.root_post_id == post.id:
                        p.root_post = post
                    if p.replied_to_id == post.id:
                        p.replied_to = post

        return (threads_posts, cursor_before, cursor_after)

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
        return self._get_list_data(
            "threads",
            limit,
            since,
            until,
            before,
            after,
        )

    def get_replies(
        self,
        limit: int = 100,
        since: str = None,
        until: str = None,
        before: str = None,
        after: str = None,
    ) -> tuple[list[ThreadPost], str, str]:
        """自身のThreads返信のリストを取得する
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
        return self._get_list_data(
            "replies",
            limit,
            since,
            until,
            before,
            after,
        )

    def get_all_posts(
        self,
        since: str = None,
        until: str = None,
    ) -> list[ThreadPost]:
        """自身のThreadsメンションのリストを取得する
        Args:
            since: いつからのデータを取得するか。例： "2025-02-11"
            until: いつまでのデータを取得するか。例： "2025-02-12"
        Returns:
            投稿のリスト
        """

        def _task(method) -> list[ThreadPost]:
            after = ""
            posts = []
            while True:
                _res, _, after = method(
                    since=since, until=until, limit=100, after=after
                )
                if after == "":
                    break
                posts.extend(_res)
            return posts

        posts = []
        with ThreadPoolExecutor() as exector:
            features = [
                exector.submit(_task, self.get_threads),
                exector.submit(_task, self.get_replies),
            ]
            for f in features:
                posts.extend(f.result())

        return posts

    def get_post(self, id: str) -> ThreadPost:
        """特定の投稿を取得する
        Args:
            id: 投稿のID
        Returns:
            投稿
        """
        res = _call_api_get(f"/{id}", [("fields", ",".join(_target_fields))])
        return _thread_data_to_dataclass(res)
