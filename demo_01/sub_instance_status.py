#!/usr/bin/env python
import subprocess


def sub_input():
    # https://docs.python.org/3/library/subprocess.html
    return subprocess.run(
        ["ssh", "root@127.0.0.1"],
        input="""
        su - oracle
        sqlplus -s / as sysdba
        set linesize 100
        set heading off
        set tab off
        select instance_name || '||' || status from v$instance;
        exit
        """,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=True,
    )


def print_output(source):
    for line in source.stdout.split("\n"):
        print(line)


def main():
    sub_data = sub_input()
    print_output(sub_data)


if __name__ == "__main__":
    main()
