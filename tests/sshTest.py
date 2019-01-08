import sys
sys.path.insert(0, '../')
from ssh import Ssh
from BufferedSsh import BufferedSsh
from Hosts import Hosts
import getpass


def main():
    username = raw_input("SSH username: ")
    # password = getpass.getpass("SSH password: ")
    password = raw_input("SSH password: ")
    host = raw_input("host: ")
    ssh = Ssh(username, password)
    ssh.connect(host)
    # hostname = ssh.findIOSHostname()
    # print hostname
    message = ssh.execute("show run int gi1/0/1")
    print message[0]
    message = ssh.execute("sis")
    print message[0]
    message = ssh.execute("config t")
    print message[1]
    ssh.disconnect()


if __name__ == "__main__":
    main()
