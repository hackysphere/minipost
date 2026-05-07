# turns out sqlite3 context doesn't close connections by itself automatically: https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager
import contextlib
import logging
import sqlite3
import time
import uuid
from typing import Literal, TypedDict

from . import config

_logger = logging.getLogger("socialapp")


class PostBase(TypedDict):
    uuid: uuid.UUID
    posted_on: int
    content: str
    user_id: uuid.UUID


class Post(PostBase):
    replies: list[PostBase] | None  # only used for the root post
    # no option to use parent_id because that is not supported (at least for now)


class ReplyReturn(TypedDict):
    reply: PostBase
    parent_id: uuid.UUID


class User(TypedDict):
    user_id: uuid.UUID
    creation_ts: int
    username: str
    token_version: int


def init_database(path: str):
    with contextlib.closing(sqlite3.connect(path)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "PRAGMA foreign_keys = true;"
        )  # this needs to be manually set in each connection editing the database because sqlite doesn't save it
        cursor.execute("""
                  CREATE TABLE IF NOT EXISTS Posts (
                        id TEXT NOT NULL UNIQUE,
                        posted_on INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        PRIMARY KEY("id"),
                        FOREIGN KEY(user_id)
                            REFERENCES Users (user_id)
                            ON DELETE CASCADE
                 )
                  """)
        cursor.execute("""
                  CREATE TABLE IF NOT EXISTS Replies (
                        id TEXT NOT NULL UNIQUE,
                        parent_id TEXT NOT NULL,
                        posted_on INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        PRIMARY KEY("id")
                        FOREIGN KEY(parent_id)
                            REFERENCES Posts (id)
                            ON DELETE CASCADE,
                        FOREIGN KEY(user_id)
                            REFERENCES Users (user_id)
                            ON DELETE CASCADE
                 )
                  """)
        cursor.execute("""
                  CREATE TABLE IF NOT EXISTS Users (
                        user_id TEXT NOT NULL UNIQUE,
                        creation_ts TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        token_version INTEGER NOT NULL,
                        PRIMARY KEY("user_id")
                 )
                  """)
        connection.commit()


def add_types_to_sql_post(sql_output: list) -> Post:
    return Post(
        uuid=uuid.UUID(sql_output[0]),
        posted_on=sql_output[1],
        content=sql_output[2],
        user_id=uuid.UUID(sql_output[3]),
        replies=None,
    )


def add_types_to_sql_reply(sql_output: list) -> PostBase:
    return PostBase(
        uuid=uuid.UUID(sql_output[0]),
        posted_on=sql_output[2],
        content=sql_output[3],
        user_id=uuid.UUID(sql_output[4]),
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

    def push_post(self, content: str, user_id: uuid.UUID) -> Post:
        post = Post(
            uuid=uuid.uuid4(),
            posted_on=time.time_ns(),  # no python floating-point weirdness
            content=content,
            user_id=user_id,
            replies=None,
        )

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = true;")
            cursor.execute(
                "INSERT INTO Posts (id, posted_on, content, user_id) VALUES (?, ?, ?, ?)",
                (
                    str(post["uuid"]),
                    post["posted_on"],
                    post["content"],
                    str(post["user_id"]),
                ),
            )
            connection.commit()

        _logger.info(f"post added with uuid {post['uuid']}")
        return post

    def push_reply(
        self, content: str, user_id: uuid.UUID, reply_to: uuid.UUID
    ) -> ReplyReturn:
        reply = PostBase(
            uuid=uuid.uuid4(),
            posted_on=time.time_ns(),  # no python floating-point weirdness
            content=content,
            user_id=user_id,
        )

        try:
            self.get_post(reply_to)
        except KeyError:
            raise KeyError(f"No post found to reply to with UUID {reply_to}")

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = true;")
            cursor.execute(
                "INSERT INTO Replies (id, parent_id, posted_on, content, user_id) VALUES (?, ?, ?, ?, ?)",
                (
                    str(reply["uuid"]),
                    str(reply_to),
                    reply["posted_on"],
                    reply["content"],
                    str(reply["user_id"]),
                ),
            )
            connection.commit()

        _logger.info(f"reply added to {reply_to} with uuid {reply['uuid']}")
        return ReplyReturn(reply=reply, parent_id=reply_to)

    def get_post(self, post_uuid: uuid.UUID) -> Post:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Posts WHERE id = ?", (str(post_uuid),))
            post = cursor.fetchone()

            if not post:
                raise KeyError(f"Post with UUID {post_uuid} not found")

            cursor.execute(
                "SELECT * FROM Replies WHERE parent_id = ?", (str(post_uuid),)
            )
            replies = cursor.fetchall()

        typed_post = add_types_to_sql_post(post)
        if replies:
            typed_post["replies"] = []
            for reply in replies:
                typed_post["replies"].append(add_types_to_sql_reply(reply))
        return typed_post

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
            cursor.execute("PRAGMA foreign_keys = true;")
            cursor.execute("DELETE FROM Posts WHERE id = ?", (str(post_uuid),))
            connection.commit()

    def delete_reply(self, reply_uuid: uuid.UUID):
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Replies WHERE id = ?", (str(reply_uuid),))
            reply = cursor.fetchone()

        if not reply:
            raise KeyError(f"Reply with UUID {reply_uuid} not found")

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = true;")
            cursor.execute("DELETE FROM Replies WHERE id = ?", (str(reply_uuid),))
            connection.commit()

    def get_posts_by_userid(self, user_id: uuid.UUID) -> list[Post]:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id FROM Posts WHERE user_id = ? ORDER BY posted_on DESC",
                (str(user_id),),
            )
            post_ids = cursor.fetchall()

        if not post_ids:
            raise KeyError(f"Posts from user with userid {user_id} not found")

        posts_typed: list[Post] = []
        for id in post_ids:
            posts_typed.append(self.get_post(id[0]))
        return posts_typed

    def create_user(self, username: str) -> User:
        user = User(
            user_id=uuid.uuid4(),
            creation_ts=time.time_ns(),
            username=username,
            token_version=1,
        )

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = true")
            cursor.execute(
                "INSERT INTO Users (user_id, creation_ts, username, token_version) VALUES (?, ?, ?, ?)",
                (
                    str(user["user_id"]),
                    user["creation_ts"],
                    user["username"],
                    user["token_version"],
                ),
            )
            connection.commit()

        return user
