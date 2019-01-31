import unittest
from Vlan import Vlan

class TestVlan(unittest.TestCase):
    def test_risque(self):
        # Vlan(risqueString='128.046.170.000/24 Public Subnet (470)').printDebug()
        # Vlan(risqueString='128.210.071.000/24 Public Subnet').printDebug()
        # Vlan(risqueString='172.021.031.000/24-VetSchoolPrintersDev (906)').printDebug()
        # Vlan(risqueString='010.162.017.000/24-STEW-CSDS-Supported_Computers_1 (1211)').printDebug()
        # Vlan(risqueString='128.046.202.000/24 Public Subnet (502)').printDebug()
        vlan1 = Vlan(risqueString='128.046.170.000/24 Public Subnet (470)')
        self.assertIsNotNone(vlan1)
        self.assertEqual(vlan1.name, 'Public Subnet')
        self.assertEqual(vlan1.ipAddress, '128.046.170.000')
        self.assertEqual(vlan1.trunk, False)
        self.assertEqual(vlan1.mask, 24)
        self.assertEqual(vlan1.tag, 470)
        vlan2 = Vlan(risqueString='128.210.071.000/24 Public Subnet')
        self.assertIsNotNone(vlan2)
        self.assertEqual(vlan2.name, 'Public Subnet')
        self.assertEqual(vlan2.ipAddress, '128.210.071.000')
        self.assertEqual(vlan2.trunk, False)
        self.assertEqual(vlan2.mask, 24)
        self.assertIsNone(vlan2.tag)
        vlan3 = Vlan(risqueString='172.021.031.000/24-VetSchoolPrintersDev (906)')
        self.assertIsNotNone(vlan3)
        self.assertEqual(vlan3.name, 'VetSchoolPrintersDev')
        self.assertEqual(vlan3.ipAddress, '172.021.031.000')
        self.assertEqual(vlan3.trunk, False)
        self.assertEqual(vlan3.mask, 24)
        self.assertEqual(vlan3.tag, 906)
        vlan4 = Vlan(risqueString='010.162.017.000/24-STEW-CSDS-Supported_Computers_1 (1211)')
        self.assertIsNotNone(vlan4)
        self.assertEqual(vlan4.name, 'STEW-CSDS-Supported_Computers_1')
        self.assertEqual(vlan4.ipAddress, '010.162.017.000')
        self.assertEqual(vlan4.trunk, False)
        self.assertEqual(vlan4.mask, 24)
        self.assertEqual(vlan4.tag, 1211)
        vlan5 = Vlan(risqueString='128.046.202.000/24 Public Subnet (502)')
        self.assertIsNotNone(vlan5)
        self.assertEqual(vlan5.name, 'Public Subnet')
        self.assertEqual(vlan5.ipAddress, '128.046.202.000')
        self.assertEqual(vlan5.trunk, False)
        self.assertEqual(vlan5.mask, 24)
        self.assertEqual(vlan5.tag, 502)
        vlan6 = Vlan(risqueString='ITIS Networks Wired Device Management Subnet (1000)')
        self.assertIsNotNone(vlan6)
        self.assertEqual(vlan6.name, 'ITIS Networks Wired Device Management Subnet')
        self.assertIsNone(vlan6.ipAddress)
        self.assertEqual(vlan6.trunk, False)
        self.assertIsNone(vlan6.mask)
        self.assertEqual(vlan6.tag, 1000)
        vlan7 = Vlan(risqueString="KRAN/RAWL Card Swipe System Private Subnet (903)")
        self.assertIsNotNone(vlan7)

        with self.assertRaises(AttributeError) as cm:
            Vlan(risqueString='')

        self.assertEqual(cm.exception.message, "risqueString is not a valid vlan")

    def test_switch(self):
        # switchport trunk native vlan 1000
        # switchport access vlan 167
        # switchport voice vlan 2981
        vlan1 = Vlan(switchString='switchport trunk native vlan 1000')
        self.assertIsNotNone(vlan1)
        self.assertEqual(vlan1.tag, 1000)
        self.assertTrue(vlan1.trunk)
        self.assertFalse(vlan1.voice)
        # self.assertEqual(vlan1.name, "")
        self.assertIsNone(vlan1.ipAddress)
        self.assertIsNone(vlan1.mask)
        vlan2 = Vlan(switchString='switchport access vlan 167')
        self.assertIsNotNone(vlan2)
        self.assertEqual(vlan2.tag, 167)
        self.assertFalse(vlan2.trunk)
        self.assertFalse(vlan2.voice)
        # self.assertEqual(vlan2.name, '')
        self.assertIsNone(vlan2.ipAddress)
        self.assertIsNone(vlan2.mask)
        vlan3 = Vlan(switchString='switchport voice vlan 2981')
        self.assertIsNotNone(vlan3)
        self.assertEqual(vlan3.tag, 2981)
        self.assertFalse(vlan3.trunk)
        self.assertTrue(vlan3.voice)
        # self.assertEqual(vlan3.name, '')
        self.assertIsNone(vlan3.ipAddress)
        self.assertIsNone(vlan3.mask)

    def test_trunkList(self):
        # list1 = Vlan.AllowedVlanList('switchport trunk allowed vlan 738,857,878,1000,1001,1307-1310,1313,1324,1325')
        # list2 = Vlan.AllowedVlanList('switchport trunk allowed vlan add 2700,3017')
        # Vlan.JoinAllowedVlanList(list1, list2)
        # for i in Vlan.JoinAllowedVlanList(list1, list2):
        # 	print i.tag
        vlans11 = [738,857,878,1000,1001,1307,1308,1309,1310,1313,1324,1325]
        vlans12 = [2700,3017]
        list11 = Vlan.AllowedVlanList('switchport trunk allowed vlan 738,857,878,1000,1001,1307-1310,1313,1324,1325')
        self.assertIsNotNone(list11)
        for vlan in vlans11:
            found = False
            for vlanObj in list11:
                if vlanObj.tag == vlan:
                    self.assertEqual(vlanObj.tag, vlan)
                    found = True
                    break
            self.assertTrue(found)

        list12 = Vlan.AllowedVlanList('switchport trunk allowed vlan add 2700,3017')
        self.assertIsNotNone(list12)
        for vlan in vlans12:
            found = False
            for vlanObj in list12:
                if vlanObj.tag == vlan:
                    self.assertEqual(vlanObj.tag, vlan)
                    found = True
                    break
            self.assertTrue(found)

        list13 = Vlan.JoinAllowedVlanList(list11, list12)
        for vlan in vlans11:
            found = False
            for vlanObj in list13:
                if vlanObj.tag == vlan:
                    self.assertEqual(vlanObj.tag, vlan)
                    found = True
                    break
            self.assertTrue(found)
        for vlan in vlans12:
            found = False
            for vlanObj in list13:
                if vlanObj.tag == vlan:
                    self.assertEqual(vlanObj.tag, vlan)
                    found = True
                    break
            self.assertTrue(found)

    def test_duplicateTrunks(self):
        vlans1 = [1]
        list1 = Vlan.AllowedVlanList('switchport trunk allowed vlan add 1,1,1')
        self.assertEqual(len(list1), len(vlans1))

        vlans2 = [1,2,3]
        list21 = Vlan.AllowedVlanList('switchport trunk allowed vlan add 1,2')
        list22 = Vlan.AllowedVlanList('switchport trunk allowed vlan add 2,3')
        list2 = Vlan.JoinAllowedVlanList(list21, list22)
        self.assertEqual(len(list2), len(vlans2))