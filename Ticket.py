from Speed import Speed
from Vlan import Vlan


class Ticket:
    speed = None
    vlan = None
    voiceVlan = None

    def __init__(self, speedString, vlanString, voiceVlanString):
        self.speed = Speed(risqueString=speedString)
        self.vlan = Vlan(risqueString=vlanString)
        self.voiceVlan = Vlan(risqueString=voiceVlanString)