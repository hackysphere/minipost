import random
import unittest
import db


class TestPostOps(unittest.TestCase):
    def setUp(self):
        self.locallist = []
        self.db = db.Database(":memory:")

        for _ in range(10):
            self.locallist.append(
                {
                    "content": str(random.random()),
                    "posted_on": random.randint(0, 100000),
                }
            )
            self.db.push_post(self.locallist[-1])

    def test_pull_posts(self):
        self.assertEqual(self.locallist, self.db.pull_posts())

    def test_pull_few_posts(self):
        self.assertEqual(self.locallist[-2:], self.db.pull_posts(2))


if __name__ == "__main__":
    unittest.main()
