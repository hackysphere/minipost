# turns out sqlite3 context doesn't close connections by itself automatically: https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager
import contextlib
import logging
import sqlite3
import time
import uuid
from typing import Literal, TypedDict

from . import config

_logger = logging.getLogger("socialapp")


class Post(TypedDict):
    uuid: uuid.UUID
    posted_on: int
    content: str
    username: str


def init_database(path: str):
    with contextlib.closing(sqlite3.connect(path)) as connection:
        cursor = connection.cursor()
        cursor.execute("""
                  CREATE TABLE IF NOT EXISTS Posts (
                        id TEXT NOT NULL UNIQUE,
                        posted_on INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        username TEXT NOT NULL,
                        PRIMARY KEY("id")
                 )
                  """)
        connection.commit()


def add_types_to_sql_post(sql_output: list):
    return Post(
        uuid=uuid.UUID(sql_output[0]),
        posted_on=sql_output[1],
        content=sql_output[2],
        username=sql_output[3],
    )


class Database:
    def __init__(
        self, path: str | Literal[":memory:"] = f"{config.DATA_FOLDER}/minipost.db"
    ) -> None:
        self.path = path
        init_database(path)
        _logger.info(f"initialized database at {path}")

    def pull_latest_posts(self, limit=-1) -> list[Post]:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM Posts ORDER BY posted_on DESC LIMIT ?", (limit,)
            )
            posts = cursor.fetchall()

        posts_typed = [add_types_to_sql_post(post) for post in posts]

        return posts_typed

    def push_post(self, content: str, user: str) -> Post:
        post = Post(
            uuid=uuid.uuid4(),
            posted_on=time.time_ns(),  # no python floating-point weirdness
            content=content,
            username=user,
        )

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Posts (id, posted_on, content, username) VALUES (?, ?, ?, ?)",
                (
                    str(post["uuid"]),
                    post["posted_on"],
                    post["content"],
                    post["username"],
                ),
            )
            connection.commit()

        _logger.info(f"post added with uuid {post['uuid']}")
        return post

    def get_post(self, post_uuid: uuid.UUID) -> Post:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Posts WHERE id = ?", (str(post_uuid),))
            post = cursor.fetchone()

        if post:
            return add_types_to_sql_post(post)
        raise KeyError(f"Post with UUID {post_uuid} not found")

    def delete_post(self, post_uuid: uuid.UUID):
        # this is probably not efficient to check if a post exists first
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Posts WHERE id = ?", (str(post_uuid),))
            post = cursor.fetchone()

        if not post:
            raise KeyError(f"Post with UUID {post_uuid} not found")

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Posts WHERE id = ?", (str(post_uuid),))
            connection.commit()

    def get_user_posts(self, username: str) -> list[Post]:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM Posts WHERE username = ? ORDER BY posted_on DESC",
                (username,),
            )
            posts = cursor.fetchall()

        if not posts:
            raise KeyError(f"Posts from user with username {username} not found")

        posts_typed = [add_types_to_sql_post(post) for post in posts]

        return posts_typed
