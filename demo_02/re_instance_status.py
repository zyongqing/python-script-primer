#!/usr/bin/env python
import re
import paramiko


def ssh_input():
    # http://docs.paramiko.org/en/2.4/api/client.html
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("127.0.0.1", 22, "root", "root", look_for_keys=False)
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
    # https://docs.python.org/3.7/howto/regex.html#regex-howto
    # https://regexr.com with PCRE mode
    pattern = re.compile(
        r"""
        (?P<name>[\w]+)     # instance name
        \|\|                # columnn delimiter with ||
        (?P<status>[\w]+)   # instance status
        """,
        re.VERBOSE,
    )

    result = {}
    for line in source:
        match = pattern.match(line.strip("\n"))
        if match:
            result[match.group("name")] = match.group("status")
    return result


def print_output(source):
    for key, status in source.items():
        print("%s is %s" % (key, status))


def main():
    ssh_data = ssh_input()
    ext_data = extract_process(ssh_data)
    print_output(ext_data)


if __name__ == "__main__":
    main()
