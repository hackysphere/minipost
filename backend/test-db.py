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

        for _ in range(10):
            self.local_posts.append(
                self.db.push_post(content=str(random.random()), user=str(uuid.uuid4()))
            )

        self.reverse_local_posts = self.local_posts[::-1]

    def tearDown(self):
        self.db_file.close()

    def test_pull_latest_posts(self):
        self.assertListEqual(self.reverse_local_posts, self.db.pull_latest_posts())

    def test_pull_few_posts(self):
        pull_amount = 2
        self.assertListEqual(
            self.reverse_local_posts[:pull_amount],
            self.db.pull_latest_posts(pull_amount),
        )

    def test_get_post_by_uuid(self):
        example_post = random.choice(self.local_posts)
        uuid = example_post["uuid"]
        self.assertDictEqual(example_post, self.db.get_post(uuid))


if __name__ == "__main__":
    unittest.main()
