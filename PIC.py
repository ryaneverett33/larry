from Speed import Speed
from Vlan import Vlan
from Provider import Provider


class PICConfig:
    voiceVlan = None
    vlan = None
    speed = None
    def __init__(self, vlan, speed):
        if type(vlan) is not str or type(speed) is not str:
            raise AttributeError("PICConfig given null attributes")
        self.vlan = Vlan(risqueString=vlan)
        self.speed = Speed(risqueString=speed)

    def addVoiceVlan(self, voiceVlan):
        if type(voiceVlan) is not str:
            raise AttributeError("addVoiceVlan given null attributes")
        self.voiceVlan = Vlan(risqueString=voiceVlan)


class PIC:
    services = None
    name = None
    provider = None
    currentConfig = None
    newConfig = None
    action = None

    def __init__(self, name, provider, action):
        if name is None or provider is None or action is None:
            raise AttributeError("PIC given null attributes")
        self.name = name
        self.action = action
        self.provider = Provider(risqueString=provider)
        self.__isValidAction()

    def applyCurrentConfig(self, voiceVlan, vlan, speed):
        if vlan is None and speed is None:
            raise AttributeError("Invalid Config, must have a vlan and a speed")
        self.currentConfig = PICConfig(vlan, speed)
        if voiceVlan is not None:
            self.currentConfig.addVoiceVlan(voiceVlan)

    def applyNewConfig(self, voiceVlan, vlan, speed):
        if vlan is None and speed is None:
            raise AttributeError("Invalid Config, must have a vlan and a speed")
        self.newConfig = PICConfig(vlan, speed)
        if voiceVlan is not None:
            self.newConfig.addVoiceVlan(voiceVlan)

    def __isValidAction(self):
        if self.action == "Activate":
            return
        elif self.action == "Deactivate":
            return
        elif self.action == "Modify":
            return
        else:
            raise ValueError("PIC given an invalid action")
