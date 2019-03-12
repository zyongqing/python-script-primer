#!/usr/bin/env python
import unittest


class MainTestCase(unittest.TestCase):
    # https://docs.python.org/3/library/unittest.html
    def setUp(self):
        print("do something before every testcase")

    def tearDown(self):
        print("do something after every testcase")

    def test_sum_with_two_int(self):
        self.assertEqual(3, 1 + 2)

    def test_sum_with_two_float(self):
        self.assertEqual(3.1, 1.2 + 1.9)


if __name__ == "__main__":
    unittest.main()
