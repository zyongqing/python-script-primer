#!/usr/bin/env python

import io
import sys
import unittest
from unittest import mock
import database_status

SSH_INPUT_INSTANCE_STANDARD = """
rac1||OPEN
""".split("\n")

SSH_INPUT_TABLESPACE_STANDARD = """
SYSTEM||ONLINE
SYSAUX||ONLINE
2 rows selected.
""".split("\n")


@mock.patch("database_status.ssh_input")
class MainTestCase(unittest.TestCase):
    # https://docs.python.org/3/library/unittest.html
    def setUp(self):
        self.stdout = io.StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_instance_success(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_INSTANCE_STANDARD
        sys.argv = "progname 127.0.0.1 22 test test instance".split()
        expect = '{"rac1": "OPEN"}\n'
        database_status.main()
        self.assertEqual(expect, self.stdout.getvalue())

    def test_tablespace_success(self, ssh_input):
        ssh_input.return_value = SSH_INPUT_TABLESPACE_STANDARD
        sys.argv = "progname 127.0.0.1 22 test test tablespace".split()
        expect = "SYSTEM, ONLINE\nSYSAUX, ONLINE\n"
        database_status.main()
        self.assertEqual(expect, self.stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
