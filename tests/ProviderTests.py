import unittest
from Provider import Provider

class ProviderTests(unittest.TestCase):
    def test_risque(self):
        # hamp-gu01a-c3750ep-01:04-Gi4/0/18
        # arms-3163-c3750ep-01:01-Gi1/0/27
        # crtn-3035b-c3850mg-02:06-Gi6/0/23
        provider1 = Provider(risqueString='hamp-gu01a-c3750ep-01:04-Gi4/0/18')
        self.assertIsNotNone(provider1)
        self.assertEqual(provider1.building, "hamp")
        self.assertEqual(provider1.TR, "gu01a")
        self.assertEqual(provider1.switchType, "c3750ep")
        self.assertEqual(provider1.intType, "Gi")
        self.assertEqual(provider1.switch, 4)
        self.assertEqual(provider1.port, 18)
        self.assertEqual(provider1.stack, 1)
        provider2 = Provider(risqueString='arms-3163-c3750ep-01:01-Gi1/0/27')
        self.assertIsNotNone(provider2)
        self.assertEqual(provider2.building, "arms")
        self.assertEqual(provider2.TR, "3163")
        self.assertEqual(provider2.switchType, "c3750ep")
        self.assertEqual(provider2.intType, "Gi")
        self.assertEqual(provider2.switch, 1)
        self.assertEqual(provider2.port, 27)
        self.assertEqual(provider2.stack, 1)
        provider3 = Provider(risqueString='crtn-3035b-c3850mg-02:06-Gi6/0/23')
        self.assertIsNotNone(provider3)
        self.assertEqual(provider3.building, "crtn")
        self.assertEqual(provider3.TR, "3035b")
        self.assertEqual(provider3.switchType, "c3850mg")
        self.assertEqual(provider3.intType, "Gi")
        self.assertEqual(provider3.switch, 6)
        self.assertEqual(provider3.port, 23)
        self.assertEqual(provider3.stack, 2)
        with self.assertRaises(AttributeError) as cm:
            Provider(risqueString='')

        self.assertEqual(cm.exception.message, "risqueString is not a valid provider!")

    def test_switch(self):
        # GigabitEthernet1/0/9
        # Gi3/0/12
        # Te1/1/3
        # Te2/3/16
        # FastEthernet0/1
        provider1 = Provider(switchString='GigabitEthernet1/0/9')
        self.assertIsNotNone(provider1)
        self.assertEqual(provider1.switch, 1)
        self.assertEqual(provider1.port, 9)
        self.assertEqual(provider1.intType, "Gi")
        self.assertFalse(provider1.uplink)
        provider2 = Provider(switchString='Gi3/0/12')
        self.assertIsNotNone(provider2)
        self.assertEqual(provider2.switch, 3)
        self.assertEqual(provider2.port, 12)
        self.assertEqual(provider2.intType, "Gi")
        self.assertFalse(provider2.uplink)
        provider3 = Provider(switchString='Te1/1/3')
        self.assertIsNotNone(provider3)
        self.assertEqual(provider3.switch, 1)
        self.assertEqual(provider3.port, 3)
        self.assertEqual(provider3.intType, "Te")
        self.assertTrue(provider3.uplink)
        with self.assertRaises(AttributeError) as cm:
            Provider(switchString='Te2/3/16')

        self.assertEqual(cm.exception.message, "switchString is a line card, not supported!")
        provider4 = Provider(switchString='FastEthernet0/1')
        self.assertIsNotNone(provider4)
        self.assertEqual(provider4.switch, 0)
        self.assertEqual(provider4.port, 1)
        self.assertEqual(provider4.intType, "Fa")
        self.assertFalse(provider4.uplink)
        with self.assertRaises(AttributeError) as cm:
            Provider(switchString='')

        self.assertEqual(cm.exception.message, "switchString is an invalid provider")
