# in theory, even if multiple imports occur, the database connections should still work because sqlite3 supports multi-reads and multi-writes through locks
# FIXME: temporary memory-based impl for now, replace with sqlite3
# WARN: this might work better if the database access object is a class

import logging
from typing import TypedDict

class Database(TypedDict):
    posts: list[Post]

class Post(TypedDict):
    posted_on: int
    content: str

_database: Database
_logger = logging.getLogger(__name__)

def init(path="./app.db"):
    # path can be :memory: in sqlite3 for tests without writing to file
    global _database
    _database = {"posts": []}
    _logger.info("initialized database")

def pull_posts(count=0):
    return _database["posts"][-count:]

def push_post(data: Post):
    _database["posts"].append(data)
    return 0

