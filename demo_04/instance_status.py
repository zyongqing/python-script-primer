#!/usr/bin/env python
import argparse
import json
import paramiko


def ssh_input(host, port, username, password):
    # http://docs.paramiko.org/en/2.4/api/client.html
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password, look_for_keys=False)
    stdin, stdout, stderr = client.exec_command(
        """
su - oracle <<EOF
sqlplus -s / as sysdba
set linesize 1000;
set heading off
set tab off
select instance_name || '||' || status from v\$instance;
exit
EOF
        """
    )
    result = stdout.readlines()
    client.close()
    return result


def extract_process(source):
    result = {}
    for line in source:
        groups = line.strip("\n").split("||")
        if groups and len(groups) == 2:
            instance_name, instance_status = groups[0], groups[1]
            result[instance_name] = instance_status
    return result


def print_json(source):
    print(json.dumps(source, indent=2))


def print_plain(source):
    for name, status in source.items():
        print("%s, %s" % (name, status))


def main():
    # https://docs.python.org/3.7/howto/argparse.html
    parser = argparse.ArgumentParser(description="check oracle instance")
    parser.add_argument("host", help="host name")
    parser.add_argument("port", help="host port", type=int)
    parser.add_argument("username", help="host username")
    parser.add_argument("password", help="host password")
    parser.add_argument("--output", help="output format",
                        choices=["json", "plain"], default="json")
    args = parser.parse_args()

    ssh_data = ssh_input(args.host, args.port, args.username, args.password)
    ext_data = extract_process(ssh_data)

    if args.output == "plain":
        print_plain(ext_data)
    else:
        print_json(ext_data)


if __name__ == "__main__":
    main()
