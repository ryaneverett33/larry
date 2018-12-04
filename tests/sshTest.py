import sys
sys.path.insert(0, '../')
from Ssh import Ssh
from BufferedSsh import BufferedSsh
from Hosts import Hosts
import getpass


def main():
    username = raw_input("SSH username: ")
    password = getpass.getpass("SSH password: ")
    host = raw_input("host: ")
    ssh = BufferedSsh(username, password)
    ssh.connect(host)
    stdin, stdout, stderr = ssh.exec_command("show run int gi1/0/1")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("show boot")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("sis")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("show aliases")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("show switch")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("sis")
    print stdout.read()
    stdout.close()
    stdin, stdout, stderr = ssh.exec_command("sis | i Te")
    print stdout.read()
    stdout.close()
    #ssh = Ssh(username, password)
    #ssh.setExpect("$")
    #ssh.connect(host)
    #print "peername: {0}".format(ssh.getPeerName())
    #print "is itap-iape: {0}".format(Hosts.isItapIape(ssh.getPeerName()))
    #print ssh.findIOSHostname()
    #print ssh.execute("show run int gi1/0/1")
    #print ssh.execute("show run int gi1/0/2")
    #print ssh.execute("sis")
    ssh.disconnect()


if __name__ == "__main__":
    main()
