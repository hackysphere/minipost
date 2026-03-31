import logging
import sqlite3
import time
import uuid
from typing import Literal, TypedDict

_logger = logging.getLogger("socialapp")


class Post(TypedDict):
    uuid: uuid.UUID
    posted_on: float
    content: str


def init_database(path: str):
    with sqlite3.connect(path) as connection:
        cursor = connection.cursor()
        cursor.execute("""
                  CREATE TABLE IF NOT EXISTS Posts (
                        id TEXT NOT NULL UNIQUE,
                        posted_on REAL NOT NULL,
                        content TEXT NOT NULL,
                        PRIMARY KEY("id")
                 )
                  """)
        connection.commit()


class Database:
    def __init__(self, path: str | Literal[":memory:"] = "./minipost.db") -> None:
        self.path = path
        init_database(path)
        _logger.info(f"initialized database at {path}")

    def pull_latest_posts(self, count=15) -> list[Post]:
        max_return = 30
        if count > max_return:
            count = max_return
        if count < 1:
            count = 1

        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM Posts ORDER BY posted_on DESC LIMIT ?", (count,)
            )
            posts = cursor.fetchall()

        posts_typed = [
            Post(
                uuid=uuid.UUID(post[0]),
                posted_on=post[1],
                content=post[2],
            )
            for post in posts
        ]

        return posts_typed

    def push_post(self, content: str) -> Post:
        post = Post(
            uuid=uuid.uuid4(),
            posted_on=time.time(),
            content=content,
        )

        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Posts (id, posted_on, content) VALUES (?, ?, ?)",
                (str(post["uuid"]), post["posted_on"], post["content"]),
            )
            connection.commit()

        _logger.info(f"post added with uuid {post['uuid']}")
        return post

    def get_post(self, post_uuid: uuid.UUID) -> Post:
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Posts WHERE id = ?", (str(post_uuid),))
            post = cursor.fetchone()

        if post:
            post_typed = Post(
                uuid=uuid.UUID(post[0]),
                posted_on=post[1],
                content=post[2],
            )
            return post_typed
        raise KeyError(f"Post with UUID {post_uuid} not found")
