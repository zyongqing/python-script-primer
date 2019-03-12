#!/usr/bin/env python


def stdin_input():
    return input("please input your name: ")


def process(data):
    return "hello %s !" % data


def stdout_output(data):
    print(data)


def main():
    stdout_output(process(stdin_input()))


if __name__ == "__main__":
    main()
