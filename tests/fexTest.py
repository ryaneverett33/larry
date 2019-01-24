import sys
sys.path.insert(0, '../')
from Ticket import Ticket
from PIC import PIC
from procedures import Config
from PasswordUtility import PasswordUtility
from ConfigurationDriver import ConfigurationDriver

def main():
    username = raw_input("SSH username: ")
    password = PasswordUtility.getpassword("SSH password: ")
    ConfigurationDriver.useTestCredentials(username, password)

    print "Running Activate Test"
    ticket = Ticket(0, None, None, None)
    pic = PIC("test", "pjis-141-c3560cx-01:01-Gi1/0/3", "pjis-141-c3560cx-01:01-Gi1/0/3", "Activate", None)
    pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (877)", "10/100T-SW-A")
    ticket.addPic(pic)
    config = Config.Config(ticket)
    config.run()

    print "Running Modify Test"
    ticket = Ticket(0, None, None, None)
    pic = PIC("test", "pjis-141-c3560cx-01:01-Gi1/0/3", "pjis-141-c3560cx-01:01-Gi1/0/3", "Modify", None)
    pic.applyCurrentConfig(None, "128.210.148.000/24 Public Subnet (877)", "10/100T-SW-A")
    pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (1)", "10/100/1000T-SW-A")
    ticket.addPic(pic)
    config = Config.Config(ticket)
    config.run()

    print "Running Deactivate Test"
    ticket = Ticket(0, None, None, None)
    pic = PIC("test", "pjis-141-c3560cx-01:01-Gi1/0/3", "pjis-141-c3560cx-01:01-Gi1/0/3", "Deactivate", None)
    pic.applyCurrentConfig(None, "128.210.148.000/24 Public Subnet (1)", "100/1000T-SW-A")
    ticket.addPic(pic)
    config = Config.Config(ticket)
    config.run()


if __name__ == "__main__":
    main()
