#!/usr/bin/env python
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
set linesize 100
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


def print_output(source):
    for line in source:
        print(line.strip("\n"))


def main():
    ssh_data = ssh_input()
    print_output(ssh_data)


if __name__ == "__main__":
    main()
