import sys
sys.path.insert(0, '../')
from Ssh import Ssh
from BufferedSshClients import BufferedSshClients
from Hosts import Hosts
import getpass

# This only works for glitch, so it can't be used
def main():
    username = raw_input("SSH username: ")
    password = getpass.getpass("SSH password: ")
    host = raw_input("host: ")
    ssh = BufferedSshClients(username, password)
    ssh.connect(host)
    stdin, stdout, stderr = ssh.exec_command("ls")
    print stdout.readlines()
    print stderr.readlines()
    stdout.close()
    stderr.close()
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
    ssh.disconnect()


if __name__ == "__main__":
    main()

