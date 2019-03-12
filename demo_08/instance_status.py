#!/usr/bin/env python
import argparse
import json
import logging
import sys
import paramiko


#    _______  __        ______   .______        ___       __        #
#   /  _____||  |      /  __  \  |   _  \      /   \     |  |       #
#  |  |  __  |  |     |  |  |  | |  |_)  |    /  ^  \    |  |       #
#  |  | |_ | |  |     |  |  |  | |   _  <    /  /_\  \   |  |       #
#  |  |__| | |  `----.|  `--'  | |  |_)  |  /  _____  \  |  `----.  #
#   \______| |_______| \______/  |______/  /__/     \__\ |_______|  #
#                                                                   #


__version__ = "1.0.0"


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
select instance_name || '||' || status from v\$instance;
exit
EOF
"""


def ssh_input(host, port, username, password):
    # http://docs.paramiko.org/en/2.4/api/client.html
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password, look_for_keys=False)
    logger.debug("[%s:%s] connect: ok", host, port)

    try:
        stdin, stdout, stderr = client.exec_command(_REMOTE_COMMAND)
        logger.debug("[%s:%s] execute: ok", host, port)

        result = stdout.readlines()
        logger.debug("input stage => %s", result)
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


def _parse(pipeline):
    for line in pipeline:
        yield line.strip("\n").split("||")


def _filter(pipeline):
    for parsed_line in pipeline:
        if len(parsed_line) == 2:
            yield parsed_line[0], parsed_line[1]


def _store(pipeline):
    return {k: v for k, v in pipeline}


def extract_process(source):
    return _store(_filter(_parse(source)))


#    ______    __    __  .___________..______    __    __  .___________.  #
#   /  __  \  |  |  |  | |           ||   _  \  |  |  |  | |           |  #
#  |  |  |  | |  |  |  | `---|  |----`|  |_)  | |  |  |  | `---|  |----`  #
#  |  |  |  | |  |  |  |     |  |     |   ___/  |  |  |  |     |  |       #
#  |  `--'  | |  `--'  |     |  |     |  |      |  `--'  |     |  |       #
#   \______/   \______/      |__|     | _|       \______/      |__|       #
#                                                                         #


def print_json(source):
    print(json.dumps(source, ensure_ascii=False))


def print_plain(source):
    for name, status in source.items():
        print("%s, %s" % (name, status))


#  .___  ___.      ___       __  .__   __.  #
#  |   \/   |     /   \     |  | |  \ |  |  #
#  |  \  /  |    /  ^  \    |  | |   \|  |  #
#  |  |\/|  |   /  /_\  \   |  | |  . `  |  #
#  |  |  |  |  /  _____  \  |  | |  |\   |  #
#  |__|  |__| /__/     \__\ |__| |__| \__|  #
#                                           #


def main():
    # https://docs.python.org/3.7/howto/argparse.html
    parser = argparse.ArgumentParser(description="check oracle instance")
    parser.add_argument("host", help="host name")
    parser.add_argument("port", help="host port", type=int)
    parser.add_argument("username", help="host username")
    parser.add_argument("password", help="host password")
    parser.add_argument("--output", help="output format",
                        choices=["json", "plain"], default="json")
    parser.add_argument("--verbose", help="debug mode", action="store_true")
    args = parser.parse_args()

    debug_logging_switch(args.verbose)

    ssh_data = ssh_input(args.host, args.port, args.username, args.password)
    ext_data = extract_process(ssh_data)
    globals()["print_%s" % args.output](ext_data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
