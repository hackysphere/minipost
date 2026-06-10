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


class AuthObject(TypedDict):
    user_id: uuid.UUID
    active: bool
    pass_hash: str
    pass_version: int


def set_up_cursor(connection: sqlite3.Connection) -> sqlite3.Cursor:
    cursor = connection.cursor()
    # this needs to be manually set in each connection editing the database because sqlite doesn't save it
    cursor.execute("PRAGMA foreign_keys = true")
    return cursor


def init_database(path: str):
    with contextlib.closing(sqlite3.connect(path)) as connection:
        cursor = set_up_cursor(connection)
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
            ) STRICT""")
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
            ) STRICT""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id TEXT NOT NULL UNIQUE,
                creation_ts TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                PRIMARY KEY("user_id")
            ) STRICT""")
        # ACTIVE should be either 0 or 1 (a "bool")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Auth (
                user_id TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL,
                pass_hash TEXT,
                pass_version INTEGER NOT NULL,
                PRIMARY KEY("user_id"),
                FOREIGN KEY(user_id)
                    REFERENCES Users (user_id)
                    ON DELETE CASCADE
            ) STRICT""")
        connection.commit()


def add_types_to_sql_post(sql_output: list) -> Post:
    return Post(
        uuid=uuid.UUID(sql_output[0]),
        posted_on=int(sql_output[1]),
        content=sql_output[2],
        user_id=uuid.UUID(sql_output[3]),
        replies=None,
    )


def add_types_to_sql_reply(sql_output: list) -> PostBase:
    return PostBase(
        uuid=uuid.UUID(sql_output[0]),
        posted_on=int(sql_output[2]),
        content=sql_output[3],
        user_id=uuid.UUID(sql_output[4]),
    )


def add_types_to_sql_user(sql_output: list) -> User:
    return User(
        user_id=uuid.UUID(sql_output[0]),
        creation_ts=int(sql_output[1]),
        username=sql_output[2],
    )


def add_types_to_sql_auth(sql_output: list) -> AuthObject:
    return AuthObject(
        user_id=uuid.UUID(sql_output[0]),
        active=bool(sql_output[1]),
        pass_hash=sql_output[2],
        pass_version=int(sql_output[3]),
    )


class Database:
    def __init__(
        self, path: str | Literal[":memory:"] = f"{config.DATA_FOLDER}/minipost.db"
    ) -> None:
        self.path = path
        init_database(path)
        _logger.info(f"initialized database at {path}")

    # ===================
    # global post getters
    # ===================

    def get_latest_posts(self, limit=-1) -> list[Post]:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute(
                "SELECT id FROM Posts ORDER BY posted_on DESC LIMIT ?", (limit,)
            )
            post_ids = cursor.fetchall()

        posts_typed: list[Post] = []
        for id in post_ids:
            posts_typed.append(self.get_post(id[0]))
        return posts_typed

    def get_posts_by_userid(self, user_id: uuid.UUID) -> list[Post]:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
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

    # ===============
    # post operations
    # ===============

    # TODO: figure out how to join the Posts and Users tables to get the usernames and such in the same row
    def get_post(self, post_uuid: uuid.UUID) -> Post:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
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

    def create_post(self, content: str, user_id: uuid.UUID) -> Post:
        post = Post(
            uuid=uuid.uuid4(),
            posted_on=time.time_ns(),  # no python floating-point weirdness
            content=content,
            user_id=user_id,
            replies=None,
        )

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
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

    def delete_post(self, post_uuid: uuid.UUID):
        # this is probably not efficient to check if a post exists first
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT id FROM Posts WHERE id = ?", (str(post_uuid),))
            post = cursor.fetchone()

            if not post:
                raise KeyError(f"Post with UUID {post_uuid} not found")

            cursor.execute("DELETE FROM Posts WHERE id = ?", (str(post_uuid),))
            connection.commit()

    # ================
    # reply operations
    # ================

    def get_reply(self, reply_uuid: uuid.UUID) -> PostBase:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT * FROM Replies WHERE id = ?", (str(reply_uuid),))
            reply = cursor.fetchone()

            if not reply:
                raise KeyError(f"Post with UUID {reply_uuid} not found")

        return add_types_to_sql_reply(reply)

    def create_reply(
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
            cursor = set_up_cursor(connection)
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

    def delete_reply(self, reply_uuid: uuid.UUID):
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT id FROM Replies WHERE id = ?", (str(reply_uuid),))
            reply = cursor.fetchone()

            if not reply:
                raise KeyError(f"Reply with UUID {reply_uuid} not found")

            cursor.execute("DELETE FROM Replies WHERE id = ?", (str(reply_uuid),))
            connection.commit()

    # ===============
    # user operations
    # ===============

    def get_user(self, user_id: uuid.UUID) -> User:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT * FROM Users WHERE user_id = ?", (str(user_id),))
            user = cursor.fetchone()

        if not user:
            raise KeyError(f"User with id {user_id} not found")

        return add_types_to_sql_user(user)

    def get_user_by_username(self, username: str) -> User:
        """
        Only use this for login, using the UUID is much better and more consistent over time
        """
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT * FROM Users WHERE username = ?", (str(username),))
            user = cursor.fetchone()

        if not user:
            raise KeyError(f"User with username {username} not found")

        return add_types_to_sql_user(user)

    def create_user(self, username: str, pass_hash: str = "") -> User:
        user = User(
            user_id=uuid.uuid4(),
            creation_ts=time.time_ns(),
            username=username,
        )

        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            try:
                cursor.execute(
                    "INSERT INTO Users (user_id, creation_ts, username) VALUES (?, ?, ?)",
                    (
                        str(user["user_id"]),
                        user["creation_ts"],
                        user["username"],
                    ),
                )
                cursor.execute(
                    "INSERT INTO Auth (user_id, active, pass_hash, pass_version) VALUES (?, ?, ?, ?)",
                    (str(user["user_id"]), 1, pass_hash, 1),
                )
                connection.commit()
            except sqlite3.IntegrityError:
                raise ValueError("Username already taken")

        return user

    def delete_user(self, user_id: uuid.UUID):
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute(
                "SELECT user_id FROM Users WHERE user_id = ?", (str(user_id),)
            )
            user = cursor.fetchone()

            if not user:
                raise KeyError(f"User with id {user_id} not found")

            cursor.execute("DELETE FROM Users WHERE user_id = ?", (str(user_id),))
            connection.commit()

    def set_user_username(self, user_id: uuid.UUID, username: str):
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute(
                "SELECT user_id FROM Users WHERE user_id = ?", (str(user_id),)
            )
            user = cursor.fetchone()

            if not user:
                raise KeyError(f"User with id {user_id} not found")

            try:
                cursor.execute(
                    "UPDATE Users SET username = ? WHERE user_id = ?",
                    (username, str(user_id)),
                )
                connection.commit()
            except sqlite3.IntegrityError:
                raise ValueError("Username already exists")

    # ===============
    # auth operations
    # ===============

    def get_auth_data(self, user_id: uuid.UUID) -> AuthObject:
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute("SELECT * FROM Auth WHERE user_id = ?", (str(user_id),))
            authobject = cursor.fetchone()

        if not authobject:
            raise KeyError(f"User with id {user_id} not found")

        return add_types_to_sql_auth(authobject)

    def set_user_status(self, user_id: uuid.UUID, active: bool):
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute(
                "SELECT user_id FROM Auth WHERE user_id = ?", (str(user_id),)
            )
            authuser = cursor.fetchone()

            if not authuser:
                raise KeyError(f"User with id {user_id} not found")

            cursor.execute(
                "UPDATE Auth SET active = ? WHERE user_id = ?",
                (int(active), str(user_id)),
            )
            connection.commit()

    def set_user_password(self, user_id: uuid.UUID, pass_hash: str):
        """
        This function DOES NOT HASH THE PASSWORD, remember to do it before storing in the database!!!
        """
        with contextlib.closing(sqlite3.connect(self.path)) as connection:
            cursor = set_up_cursor(connection)
            cursor.execute(
                "SELECT pass_version FROM Auth WHERE user_id = ?", (str(user_id),)
            )
            authobject = cursor.fetchone()

            if not authobject:
                raise KeyError(f"User with id {user_id} not found")
            new_pass_version: int = authobject[0] + 1

            cursor.execute(
                "UPDATE Auth SET pass_hash = ?, pass_version = ? WHERE user_id = ?",
                (pass_hash, new_pass_version, str(user_id)),
            )
            connection.commit()
