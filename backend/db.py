# in theory, even if multiple imports occur, the database connections should still work because sqlite3 supports multi-reads and multi-writes through locks
# FIXME: temporary memory-based impl for now, replace with sqlite3

import logging
from typing import TypedDict, Literal

_logger = logging.getLogger(__name__)


class DBSchema(TypedDict):
    posts: list[Post]


class Post(TypedDict):
    posted_on: int
    content: str


class Database:
    def __init__(self, path: str | Literal[":memory:"] = "./app.db") -> None:
        # path can be :memory: in sqlite3 for tests without writing to file
        self.database: DBSchema = {"posts": []}
        _logger.info("initialized database")

    def pull_posts(self, count=0) -> list[Post]:
        return self.database["posts"][-count:]

    def push_post(self, data: Post) -> int:
        self.database["posts"].append(data)
        return 0

