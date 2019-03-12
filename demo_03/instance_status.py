#!/usr/bin/env python
import json
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
    result = {}
    for line in source:
        groups = line.strip("\n").split("||")
        if groups and len(groups) == 2:
            instance_name, instance_status = groups[0], groups[1]
            result[instance_name] = instance_status
    return result


def print_json(source):
    print(json.dumps(source, indent=2))


def main():
    ssh_data = ssh_input()
    ext_data = extract_process(ssh_data)
    print_json(ext_data)


if __name__ == "__main__":
    main()
