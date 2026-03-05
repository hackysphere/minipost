import random
import unittest
import db


class TestPostOps(unittest.TestCase):
    def setUp(self):
        self.localposts: list[db.Post] = []
        self.db = db.Database(":memory:")

        for _ in range(10):
            self.localposts.append(self.db.push_post(str(random.random())))

    def test_pull_latest_posts(self):
        self.assertListEqual(self.localposts, self.db.pull_latest_posts())

    def test_pull_few_posts(self):
        pull_amount = 2
        self.assertListEqual(
            self.localposts[-pull_amount:], self.db.pull_latest_posts(pull_amount)
        )

    def test_get_post_by_uuid(self):
        examplepost = random.choice(self.localposts)
        uuid = examplepost["uuid"]
        self.assertDictEqual(examplepost, self.db.get_post(uuid))


if __name__ == "__main__":
    unittest.main()
