#!/usr/bin/env python
import argparse
import functools
import json
import logging
import sys
import paramiko
from config import RULES

#    _______  __        ______   .______        ___       __        #
#   /  _____||  |      /  __  \  |   _  \      /   \     |  |       #
#  |  |  __  |  |     |  |  |  | |  |_)  |    /  ^  \    |  |       #
#  |  | |_ | |  |     |  |  |  | |   _  <    /  /_\  \   |  |       #
#  |  |__| | |  `----.|  `--'  | |  |_)  |  /  _____  \  |  `----.  #
#   \______| |_______| \______/  |______/  /__/     \__\ |_______|  #
#                                                                   #


__version__ = "1.0.0"


def plugin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug("init pipeline %s", f.__name__)
        for line in f(*args, **kwargs):
            logger.debug('%s => "%r"', f.__name__, line)
            yield line
    return wrapper


def pull(**kwargs):
    host = kwargs.get("host")
    port = kwargs.get("port")
    username = kwargs.get("username")
    password = kwargs.get("password")
    item = kwargs.get("item")

    previous_pipe = [host, port, username, password]
    rule = RULES[item]

    # init all pipeline
    for each_pipe in rule["pipes"]:
        each_pipe_callable = globals()[each_pipe]
        previous_pipe = each_pipe_callable(previous_pipe, **rule)

    # pull from last pipeline
    for _ in previous_pipe:
        pass


#   __        ______     _______   _______  __  .__   __.   _______   #
#  |  |      /  __  \   /  _____| /  _____||  | |  \ |  |  /  _____|  #
#  |  |     |  |  |  | |  |  __  |  |  __  |  | |   \|  | |  |  __    #
#  |  |     |  |  |  | |  | |_ | |  | |_ | |  | |  . `  | |  | |_ |   #
#  |  `----.|  `--'  | |  |__| | |  |__| | |  | |  |\   | |  |__| |   #
#  |_______| \______/   \______|  \______| |__| |__| \__|  \______|   #
#                                                                     #


# https://docs.python.org/3.7/howto/logging.html
logging.basicConfig(format="%(levelname)s\t%(asctime)s\t%(message)s")
logger = logging.getLogger(__name__)


def debug_logging_switch(is_turn_on):
    if is_turn_on:
        logger.setLevel(logging.DEBUG)
    else:
        default_level = logging.getLogger().getEffectiveLevel()
        logger.setLevel(default_level)


#   __  .__   __. .______    __    __  .___________.  #
#  |  | |  \ |  | |   _  \  |  |  |  | |           |  #
#  |  | |   \|  | |  |_)  | |  |  |  | `---|  |----`  #
#  |  | |  . `  | |   ___/  |  |  |  |     |  |       #
#  |  | |  |\   | |  |      |  `--'  |     |  |       #
#  |__| |__| \__| | _|       \______/      |__|       #
#                                                     #


_REMOTE_COMMAND = """
su - oracle <<EOF
sqlplus -s / as sysdba
set linesize 1000;
set heading off
set tab off
%s
exit
EOF
"""


@plugin
def ssh_input(pipeline, **kwargs):
    host, port, username, password = pipeline
    sql = kwargs["sql"]

    # http://docs.paramiko.org/en/2.4/api/client.html
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password, look_for_keys=False)
    logger.debug("[%s:%s] connect: ok", host, port)

    try:
        remote_command = _REMOTE_COMMAND % sql
        stdin, stdout, stderr = client.exec_command(remote_command)
        logger.debug("[%s:%s] execute: ok", host, port)

        result = stdout.readlines()
        logger.debug("[%s:%s] result: %s", host, port, result)
        return result
    finally:
        client.close()
        logger.debug("[%s:%s] close: ok", host, port)


#  .______   .______        ______     ______   #
#  |   _  \  |   _  \      /  __  \   /      |  #
#  |  |_)  | |  |_)  |    |  |  |  | |  ,----'  #
#  |   ___/  |      /     |  |  |  | |  |       #
#  |  |      |  |\  \----.|  `--'  | |  `----.  #
#  | _|      | _| `._____| \______/   \______|  #
#                                               #


@plugin
def parse_proc(pipeline, **kwargs):
    for line in pipeline:
        yield line.strip("\n").split("||")


@plugin
def filter_proc(pipeline, **kwargs):
    for line in pipeline:
        if len(line) == 2:
            yield line


@plugin
def slide_proc(pipeline, **kwargs):
    for line in pipeline:
        yield line[:2]


@plugin
def dict_proc(pipeline, **kwargs):
    for line in pipeline:
        yield line[0], line[1]


#    ______    __    __  .___________..______    __    __  .___________.  #
#   /  __  \  |  |  |  | |           ||   _  \  |  |  |  | |           |  #
#  |  |  |  | |  |  |  | `---|  |----`|  |_)  | |  |  |  | `---|  |----`  #
#  |  |  |  | |  |  |  |     |  |     |   ___/  |  |  |  |     |  |       #
#  |  `--'  | |  `--'  |     |  |     |  |      |  `--'  |     |  |       #
#   \______/   \______/      |__|     | _|       \______/      |__|       #
#                                                                         #


@plugin
def print_json(pipeline, **kwargs):
    print(json.dumps(dict(pipeline), ensure_ascii=False))
    yield "finished"


@plugin
def print_plain(pipeline, **kwargs):
    for name, status in pipeline:
        print("%s, %s" % (name, status))
    yield "finished"


#  .___  ___.      ___       __  .__   __.  #
#  |   \/   |     /   \     |  | |  \ |  |  #
#  |  \  /  |    /  ^  \    |  | |   \|  |  #
#  |  |\/|  |   /  /_\  \   |  | |  . `  |  #
#  |  |  |  |  /  _____  \  |  | |  |\   |  #
#  |__|  |__| /__/     \__\ |__| |__| \__|  #
#                                           #


def main():
    # https://docs.python.org/3.7/howto/argparse.html
    parser = argparse.ArgumentParser(description="check oracle status")
    parser.add_argument("host", help="host name")
    parser.add_argument("port", help="host port", type=int)
    parser.add_argument("username", help="host username")
    parser.add_argument("password", help="host password")
    parser.add_argument("item", help="status item name", choices=RULES.keys())
    parser.add_argument("--verbose", help="debug mode", action="store_true")
    args = parser.parse_args()

    debug_logging_switch(args.verbose)
    pull(**vars(args))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
