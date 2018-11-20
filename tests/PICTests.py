import unittest
from PIC import PIC
from Vlan import Vlan

class PICTests(unittest.TestCase):
    def test_PIC(self):
        pic = PIC('GCMB-103-B', 'gcmb-100-c3560cg-01-Gi0/6', 'Activate')
        pic.applyNewConfig(None, '128.210.021.000/24 Public Subnet (21)', '10/100/1000T-SW-A')
        self.assertEqual(pic.newConfig.vlan.tag, 21)
        self.assertEqual(pic.newConfig.vlan.ipAddress, '128.210.021.000')
        self.assertEqual(pic.newConfig.speed.speedTuple[0], 10)
        self.assertEqual(pic.newConfig.speed.speedTuple[1], 100)
        self.assertEqual(pic.newConfig.speed.speedTuple[2], 1000)
        pic2 = PIC('MJIS-1063HW-UPS', 'mjis-1063-c9348uxm-01:01-Te1/0/48', 'Modify')
        pic2.applyCurrentConfig(None, 'ITIS Networks Wired Device Management Subnet (1000)', '100T-SW-F')
        pic2.applyNewConfig(None, 'ITIS Networks Wired Device Management Subnet (1000)', '100/1000/2.5G/5G/10G-SW-A')
        self.assertTrue(Vlan.equal(pic2.currentConfig.vlan, pic2.newConfig.vlan))
        self.assertEqual(pic2.currentConfig.vlan.tag, 1000)
        self.assertEqual(pic2.currentConfig.speed.speedTuple[1], 100)
        self.assertEqual(pic2.newConfig.speed.speedTuple[1], 100)
        self.assertEqual(pic2.newConfig.speed.speedTuple[5], 10000)
