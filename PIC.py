from Speed import Speed
from Vlan import Vlan
from Provider import Provider

class PIC:
    speed = None
    vlan = None
    voiceVlan = None
    services = None
    name = None;
    provider = None

    def __init__(self, speedString, vlanString, voiceVlanString, name, provider):
        self.speed = Speed(risqueString=speedString)
        self.vlan = Vlan(risqueString=vlanString)
        self.voiceVlan = Vlan(risqueString=voiceVlanString)
        self.name = name
