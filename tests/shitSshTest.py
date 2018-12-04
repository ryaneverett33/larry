import sys
sys.path.insert(0, '../')
from shitSsh import shitSsh
from Hosts import Hosts
import getpass
import paramiko

def main():
    username = raw_input("SSH username: ")
    password = getpass.getpass("SSH password: ")
    host = raw_input("host: ")
    # ssh = shitSsh(username, password)
    # stdin, stdout, stderr = ssh.execute("ls", host)
    # print stdout.read()
    # stdout.close()
    print shitSsh.execute("show run int gi1/0/1", host, username, password)
    print shitSsh.execute("sis", host, username, password)
    print shitSsh.execute("show running-config", host, username, password)
    print shitSsh.execute("show switch", host, username, password)
    print shitSsh.execute("show vlans", host, username, password)

    # stdin, stdout, stderr = ssh.exec_command("show boot")
    # print stdout.read()
    # stdout.close()
    # stdin, stdout, stderr = ssh.exec_command("sis")
    # print stdout.read()
    # stdout.close()
    # stdin, stdout, stderr = ssh.exec_command("show aliases")
    # print stdout.read()
    # stdout.close()
    # stdin, stdout, stderr = ssh.exec_command("show switch")
    # print stdout.read()
    # stdout.close()
    # stdin, stdout, stderr = ssh.exec_command("sis")
    # print stdout.read()
    # stdout.close()
    # stdin, stdout, stderr = ssh.exec_command("sis | i Te")
    # print stdout.read()
    # stdout.close()
    # ssh.disconnect()


if __name__ == "__main__":
    main()

