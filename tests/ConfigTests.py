import unittest
from ConfigurationDriver import ConfigurationDriver
from Ticket import Ticket
from PIC import PIC
from procedures import Config
from Hosts import Hosts


class ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ConfigurationDriver.useTestCredentials("", "")
        Hosts.USE_DEBUG = True

    def test_basicModify(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("210c-SPARE", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Modify", None)
        pic.applyCurrentConfig(None, "128.210.148.000/24 Public Subnet (1998)", "10/100/1000T-SW-A")
        pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (1998)", "10/100/1000T-SW-A")
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()

    def test_basicActivate(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("210c-spare", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Activate", None)
        pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (1998)", "100/1000T-SW-A")
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()

    def test_basicDeactivate(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("210c-spare", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Deactivate", None)
        pic.applyCurrentConfig(None, "128.210.148.000/24 Public Subnet (1998)", "100/1000T-SW-A")
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()

    def test_trunkModify(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("trunk-test", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Modify", None)
        pic.applyCurrentConfig(None, ["128.210.148.000/24 Public Subnet (2)", "128.210.148.000/24 Public Subnet (3)", "128.210.148.000/24 Public Subnet (4)"], "100/1000T-SW-A")
        pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (2)", "1000T-SW-A")
        pic.addTaggedVlans(["128.210.148.000/24 Public Subnet (3)", "128.210.148.000/24 Public Subnet (4)", "128.210.148.000/24 Public Subnet (5)"])
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()

    def test_trunkActivate(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("trunk-test", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Activate", None)
        pic.applyNewConfig(None, "128.210.148.000/24 Public Subnet (2)", "10/100/1000T-SW-A")
        pic.addTaggedVlans(["128.210.148.000/24 Public Subnet (3)", "128.210.148.000/24 Public Subnet (5)"])
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()

    def test_trunkDeactivate(self):
        ticket = Ticket(0, None, None, None)
        pic = PIC("trunk-test", "tel-210c-c3560cx-01:01-Gi1/0/10", "tel-210c-c3560cx-01:01-Gi1/0/10", "Deactivate", None)
        pic.applyCurrentConfig(None, ["128.210.148.000/24 Public Subnet (2)", "128.210.148.000/24 Public Subnet (3)",
                                      "128.210.148.000/24 Public Subnet (4)"], "100/1000T-SW-A")
        ticket.addPic(pic)
        config = Config.Config(ticket)
        config.run()
