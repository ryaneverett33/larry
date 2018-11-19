import unittest
from Speed import Speed


class TestSpeed(unittest.TestCase):

    def test_name(self):
        # Speed(name='10')
        # Speed(name='Gigabit')
        tenSpeed = Speed(name='10')
        self.assertIsNotNone(tenSpeed)
        self.assertIs(tenSpeed.name, Speed.NAME_TEN)
        self.assertIs(tenSpeed.duplex, Speed.DUPLEX_AUTO)
        self.assertEqual(tenSpeed.speedTuple[0], 10)
        gigSpeed = Speed(name='Gigabit')
        self.assertIsNotNone(gigSpeed)
        self.assertIs(gigSpeed.name, Speed.NAME_GIGABIT)
        self.assertIs(gigSpeed.duplex, Speed.DUPLEX_AUTO)
        self.assertEqual(gigSpeed.speedTuple[0], 10)
        self.assertEqual(gigSpeed.speedTuple[1], 100)
        self.assertEqual(gigSpeed.speedTuple[2], 1000)
        with self.assertRaises(AttributeError) as cm:
            Speed(name='')

        self.assertEqual(cm.exception.message, "name is an invalid type")

    def test_risque(self):
        # Speed(risqueString='10/100/1000T-SW-A')
        # Speed(risqueString='100/1000T-SW-A')
        # Speed(risqueString='100/1000/2.5G/5G/10G-SW-A')
        gigSpeed = Speed(risqueString='10/100/1000T-SW-A')
        self.assertIsNotNone(gigSpeed)
        self.assertIs(gigSpeed.duplex, Speed.DUPLEX_AUTO)
        self.assertEqual(gigSpeed.speedTuple[0], 10)
        self.assertEqual(gigSpeed.speedTuple[1], 100)
        self.assertEqual(gigSpeed.speedTuple[2], 1000)
        tenHundred = Speed(risqueString='100/1000T-SW-A')
        self.assertIsNotNone(tenHundred)
        self.assertIs(tenHundred.duplex, Speed.DUPLEX_AUTO)
        self.assertEqual(tenHundred.speedTuple[1], 100)
        self.assertEqual(tenHundred.speedTuple[2], 1000)
        tenGig = Speed(risqueString='100/1000/2.5G/5G/10G-SW-A')
        self.assertIsNotNone(tenGig)
        self.assertIs(tenGig.duplex, Speed.DUPLEX_AUTO)
        self.assertEqual(tenGig.speedTuple[1], 100)
        self.assertEqual(tenGig.speedTuple[2], 1000)
        self.assertEqual(tenGig.speedTuple[3], 2500)
        self.assertEqual(tenGig.speedTuple[4], 5000)
        self.assertEqual(tenGig.speedTuple[5], 10000)
        with self.assertRaises(AttributeError) as cm:
            Speed(risqueString='')

        self.assertEqual(cm.exception.message, "Risque String is not supported! Error: Speed")

    def test_switch(self):
        # Speed(switchString='speed auto 10 100')
        # Speed(switchString='speed 1000')
        # Speed(switchString='speed auto 100 1000')
        # Speed(switchString='')
        tenHundred = Speed(switchString='speed auto 10 100')
        self.assertIsNotNone(tenHundred)
        self.assertIs(tenHundred.speedAuto, True)
        self.assertEqual(tenHundred.speedTuple[0], 10)
        self.assertEqual(tenHundred.speedTuple[1], 100)
        thousand = Speed(switchString='speed 1000')
        self.assertIsNotNone(thousand)
        self.assertIs(thousand.speedAuto, False)
        self.assertEqual(thousand.speedTuple[2], 1000)
        hundredThousand = Speed(switchString='speed auto 100 1000')
        self.assertIsNotNone(hundredThousand)
        self.assertIs(hundredThousand.speedAuto, True)
        self.assertEqual(hundredThousand.speedTuple[1], 100)
        self.assertEqual(hundredThousand.speedTuple[2], 1000)
        empty = Speed(switchString='')
        self.assertIsNotNone(empty)
        self.assertIs(empty.speedAuto, True)
        self.assertEqual(empty.speedTuple[1], 0)
        self.assertEqual(empty.speedTuple[2], 0)
