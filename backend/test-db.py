import random
import tempfile
import unittest
import uuid

from app import db


class TestPostOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        self.local_posts: list[db.Post] = []

        for _ in range(100):
            newuser = self.db.create_user(username=str(uuid.uuid4()))
            self.local_posts.append(
                self.db.create_post(
                    content=str(random.random()), user_id=newuser["user_id"]
                )
            )

        self.local_posts = self.local_posts[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_pull_latest_posts(self):
        self.assertListEqual(self.local_posts, self.db.get_latest_posts())

    def test_pull_few_posts(self):
        pull_amount = 2
        self.assertListEqual(
            self.local_posts[:pull_amount],
            self.db.get_latest_posts(pull_amount),
        )

    def test_get_post_by_uuid(self):
        example_post = random.choice(self.local_posts)
        uuid = example_post["uuid"]
        self.assertDictEqual(example_post, self.db.get_post(uuid))

    def test_delete_post_by_uuid(self):
        example_post = random.choice(self.local_posts)
        uuid = example_post["uuid"]
        self.db.delete_post(uuid)
        self.assertRaises(KeyError, lambda: self.db.get_post(uuid))


class TestReplyOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)

        self.user = self.db.create_user(str(random.random()))
        self.post_uuid = self.db.create_post(
            content=str(random.random()), user_id=self.user["user_id"]
        )["uuid"]

        self.reply_user_id = self.db.create_user(username=str(random.random()))[
            "user_id"
        ]
        self.reply = self.db.create_reply(
            content=str(random.random()),
            user_id=self.reply_user_id,
            reply_to=self.post_uuid,
        )
        self.reply_uuid = self.reply["uuid"]

    def tearDown(self):
        self.db_file.close()

    def test_get_empty_reply_param(self):
        newpost = self.db.create_post(
            content=str(random.random()), user_id=self.user["user_id"]
        )
        self.assertIsNone(self.db.get_post(newpost["uuid"])["replies"])

    def test_get_reply(self):
        self.assertEqual(self.db.get_reply(self.reply_uuid), self.reply)

    def test_get_reply_from_post(self):
        dbpost = self.db.get_post(self.post_uuid)
        if not dbpost["replies"]:
            self.fail("No replies found in post")

        self.assertEqual(self.reply_uuid, dbpost["replies"][0]["uuid"])

    def test_delete_reply(self):
        self.db.delete_reply(self.reply_uuid)
        self.assertIsNone(self.db.get_post(self.post_uuid)["replies"])


class TestUserOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        self.posts_user1: list[db.Post] = []
        self.user1 = self.db.create_user(username=str(uuid.uuid4()))

        for _ in range(100):
            self.posts_user1.append(
                self.db.create_post(
                    content=str(random.random()), user_id=self.user1["user_id"]
                )
            )

        self.posts_user1 = self.posts_user1[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_get_user_posts(self):
        self.assertListEqual(
            self.db.get_posts_by_userid(self.user1["user_id"]),
            self.posts_user1,
        )

    def test_get_user_data(self):
        self.assertEqual(self.db.get_user(self.user1["user_id"]), self.user1)

    def test_get_user_data_by_username(self):
        self.assertEqual(
            self.db.get_user_by_username(self.user1["username"]), self.user1
        )

    def test_delete_user(self):
        self.db.delete_user(self.user1["user_id"])
        self.assertRaises(KeyError, lambda: self.db.get_user(self.user1["user_id"]))

    def test_set_user_username(self):
        username = str(random.random())
        self.db.set_user_username(self.user1["user_id"], username)
        self.assertEqual(username, self.db.get_user(self.user1["user_id"])["username"])


class TestAuthOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)

        self.password = str(random.random())
        self.user_id = self.db.create_user(str(random.random()), self.password)[
            "user_id"
        ]

    def tearDown(self):
        self.db_file.close()

    def test_get_auth_data(self):
        authobject = db.AuthObject(
            user_id=self.user_id,
            active=True,
            pass_hash=self.password,
            pass_version=1,
        )
        self.assertEqual(authobject, self.db.get_auth_data(self.user_id))

    def test_set_user_status(self):
        self.db.set_user_status(self.user_id, False)
        self.assertEqual(False, self.db.get_auth_data(self.user_id)["active"])
        self.db.set_user_status(self.user_id, True)
        self.assertEqual(True, self.db.get_auth_data(self.user_id)["active"])

    def test_set_user_password(self):
        # note: this doesn't save a password *hash*, but argon2 hashes are strings, so this should still work in any case

        authdata = self.db.get_auth_data(self.user_id)
        self.assertEqual(self.password, authdata["pass_hash"])
        self.assertEqual(1, authdata["pass_version"])

        new_password = str(random.random())
        self.db.set_user_password(self.user_id, new_password)
        authdata = self.db.get_auth_data(self.user_id)

        self.assertEqual(new_password, authdata["pass_hash"])
        self.assertEqual(2, authdata["pass_version"])


if __name__ == "__main__":
    unittest.main()
