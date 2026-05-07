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


class TestUserOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        self.posts_user1: list[db.Post] = []
        self.posts_user2: list[db.Post] = []
        self.user1 = self.db.create_user(username=str(uuid.uuid4()))
        self.user2 = self.db.create_user(username=str(uuid.uuid4()))

        for _ in range(100):
            self.posts_user1.append(
                self.db.create_post(
                    content=str(random.random()), user_id=self.user1["user_id"]
                )
            )
            self.posts_user2.append(
                self.db.create_post(
                    content=str(random.random()), user_id=self.user2["user_id"]
                )
            )

        self.posts_user1 = self.posts_user1[::-1]
        self.posts_user2 = self.posts_user2[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_get_user_posts(self):
        self.assertListEqual(
            self.db.get_posts_by_userid(self.user1["user_id"]),
            self.posts_user1,
        )
        self.assertListEqual(
            self.db.get_posts_by_userid(self.user2["user_id"]),
            self.posts_user2,
        )

    def test_get_user_data(self):
        self.assertEqual(self.db.get_user(self.user1["user_id"]), self.user1)
        self.assertEqual(self.db.get_user(self.user2["user_id"]), self.user2)

    def test_delete_user(self):
        self.db.delete_user(self.user1["user_id"])
        self.assertRaises(KeyError, lambda: self.db.get_user(self.user1["user_id"]))


class TestReplyOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        user = self.db.create_user(str(random.random()))
        self.post_uuid = self.db.create_post(
            content=str(random.random()), user_id=user["user_id"]
        )["uuid"]

    def tearDown(self):
        self.db_file.close()

    def test_get_empty_reply_param(self):
        self.assertIsNone(self.db.get_post(self.post_uuid)["replies"])

    def test_get_reply(self):
        reply_user_id = self.db.create_user(username=str(random.random()))["user_id"]
        reply_uuid = self.db.create_reply(
            content=str(random.random()),
            user_id=reply_user_id,
            reply_to=self.post_uuid,
        )["reply"]["uuid"]

        dbpost = self.db.get_post(self.post_uuid)
        if not dbpost["replies"]:
            self.fail("No replies found in post")

        self.assertEqual(reply_uuid, dbpost["replies"][0]["uuid"])

    def test_delete_reply(self):
        reply_user_id = self.db.create_user(username=str(random.random()))["user_id"]
        reply_uuid = self.db.create_reply(
            content=str(random.random()),
            user_id=reply_user_id,
            reply_to=self.post_uuid,
        )["reply"]["uuid"]

        self.db.delete_reply(reply_uuid)
        self.assertIsNone(self.db.get_post(self.post_uuid)["replies"])


if __name__ == "__main__":
    unittest.main()
