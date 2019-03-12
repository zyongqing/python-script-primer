#!/usr/bin/env python

import io
import sys
import unittest
from unittest import mock
import instance_status

SSH_INPUT_STANDARD = """
rac1||OPEN
""".split("\n")

SSH_INPUT_NOROWS = """
no rows
""".split("\n")

SSH_INPUT_CHINESE = """
rac1||在线
""".split("\n")


@mock.patch("instance_status.ssh_input")
class MainTestCase(unittest.TestCase):
    # https://docs.python.org/3/library/unittest.html
    def setUp(self):
        self.stdout = io.StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_instance_success_with_json_output(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_STANDARD
        sys.argv = "progname 127.0.0.1 22 test test --output json".split()
        expect = '{"rac1": "OPEN"}\n'
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_instance_success_with_plain_output(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_STANDARD
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        expect = "rac1, OPEN\n"
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_input_stage_with_correct_arguments(self, ssh_input):
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        instance_status.main()
        ssh_input.assert_called_once_with("127.0.0.1", 22, "test", "test")

    def test_input_stage_with_no_data(self, ssh_input):
        ssh_input.return_value = [""]
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        expect = ""
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_input_stage_with_no_match_rows(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_NOROWS
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        expect = ""
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_input_stage_with_exception(self, ssh_input):
        ssh_input.side_effect = Exception("Oops! something wrong.")
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        with self.assertRaises(Exception):
            instance_status.main()

    def test_input_stage_with_chinese_and_json_output(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_CHINESE
        sys.argv = "progname 127.0.0.1 22 test test --output json".split()
        expect = '{"rac1": "在线"}\n'
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_input_stage_with_chinese_and_plain_output(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_CHINESE
        sys.argv = "progname 127.0.0.1 22 test test --output plain".split()
        expect = "rac1, 在线\n"
        instance_status.main()
        self.assertEqual(expect, self.stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
