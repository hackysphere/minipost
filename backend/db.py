# in theory, even if multiple imports occur, the database connections should still work because sqlite3 supports multi-reads and multi-writes through locks
# FIXME: temporary memory-based impl for now, replace with sqlite3
import time
import logging
import uuid
from typing import TypedDict, Literal

_logger = logging.getLogger(__name__)


class DBSchema(TypedDict):
    posts: list[Post]


class Post(TypedDict):
    uuid: uuid.UUID
    posted_on: int
    content: str


class Database:
    def __init__(self, path: str | Literal[":memory:"] = "./app.db") -> None:
        # path can be :memory: in sqlite3 for tests without writing to file
        self.database: DBSchema = DBSchema(posts=[])
        _logger.info("initialized database")

    def pull_latest_posts(self, count=15) -> list[Post]:
        max_return = 30
        if count > max_return:
            count = max_return
        return self.database["posts"][-count:]

    def push_post(self, content: str) -> Post:
        post = Post(
            uuid=uuid.uuid4(),
            posted_on=int(time.time()),
            content=content,
        )
        self.database["posts"].append(post)
        return post

    def get_post(self, uuid: uuid.UUID) -> Post:
        for post in self.database["posts"]:
            if post["uuid"] == uuid:
                return post
        raise KeyError("Post with given UUID not found")
