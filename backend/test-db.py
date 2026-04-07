import random
import tempfile
import unittest
import uuid

from app import db, constants


class TestPostOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        self.local_posts: list[db.Post] = []

        for _ in range(100):
            self.local_posts.append(
                self.db.push_post(content=str(random.random()), user=str(uuid.uuid4()))
            )

        self.local_posts = self.local_posts[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_pull_latest_posts(self):
        self.assertListEqual(self.local_posts[:15], self.db.pull_latest_posts())

    def test_pull_few_posts(self):
        pull_amount = 2
        self.assertListEqual(
            self.local_posts[:pull_amount],
            self.db.pull_latest_posts(pull_amount),
        )

    def test_get_post_by_uuid(self):
        example_post = random.choice(self.local_posts)
        uuid = example_post["uuid"]
        self.assertDictEqual(example_post, self.db.get_post(uuid))


class TestUsernameOps(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        self.db = db.Database(self.db_file.name)
        self.posts_user1: list[db.Post] = []
        self.posts_user2: list[db.Post] = []
        self.user1 = str(uuid.uuid4())
        self.user2 = str(uuid.uuid4())

        for _ in range(100):
            self.posts_user1.append(
                self.db.push_post(content=str(random.random()), user=self.user1)
            )
            self.posts_user2.append(
                self.db.push_post(content=str(random.random()), user=self.user2)
            )

        self.posts_user1 = self.posts_user1[::-1]
        self.posts_user2 = self.posts_user2[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_get_user_posts(self):
        self.assertListEqual(
            self.db.get_user_posts(self.user1),
            self.posts_user1[: constants.USER_MAX_POSTS],
        )
        self.assertListEqual(
            self.db.get_user_posts(self.user2),
            self.posts_user2[: constants.USER_MAX_POSTS],
        )


if __name__ == "__main__":
    unittest.main()
