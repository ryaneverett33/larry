import unittest
from Patch import Patch


class PatchTests(unittest.TestCase):

    def test_risque(self):
        patch1 = Patch(risqueString="frny-4001a-pp24-04-19 (back)")
        self.assertEqual(patch1.building, "frny")
        self.assertEqual(patch1.room, "4001a")
        self.assertEqual(patch1.patchType, "pp24")
        self.assertEqual(patch1.panelNumber, 4)
        self.assertEqual(patch1.portNumber, 19)
        patch2 = Patch(risqueString="bown-1111a-c6pp24-01-13 (back)")
        self.assertEqual(patch2.building, "bown")
        self.assertEqual(patch2.room, "1111a")
        self.assertEqual(patch2.patchType, "c6pp24")
        self.assertEqual(patch2.panelNumber, 1)
        self.assertEqual(patch2.portNumber, 13)
