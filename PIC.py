from Speed import Speed
from Vlan import Vlan
from Provider import Provider


class PICConfig:
    voiceVlan = None
    vlan = None     # Can be an array
    vlanList = False
    speed = None

    def __init__(self, vlan, speed):
        if type(speed) is not str or vlan is None:
            raise AttributeError("PICConfig given null attributes")
        if type(vlan) is str:
            self.vlan = Vlan(risqueString=vlan)
            self.vlanList = False
        elif isinstance(vlan, list):
            self.vlan = []
            for v in vlan:
                self.vlan.append(Vlan(risqueString=v))
            self.vlanList = True
        self.speed = Speed(risqueString=speed)

    def addVoiceVlan(self, voiceVlan):
        if type(voiceVlan) is not str:
            raise AttributeError("addVoiceVlan given null attributes")
        self.voiceVlan = Vlan(risqueString=voiceVlan)

    # returns a new PICConfig of the differences between two configs, null if the same
    @staticmethod
    def diffConfig(oldConfig, newConfig):
        if oldConfig is None or newConfig is None:
            raise AttributeError("diffConfig given null attributes")
        if not isinstance(oldConfig, PICConfig) or not isinstance(newConfig, PICConfig):
            raise AttributeError("diffConfig can't diff objects that aren't of type PICConfig")


class PIC:
    services = None
    name = None
    currentProvider = None
    newProvider = None
    currentConfig = None
    newConfig = None
    action = None

    def __init__(self, name, currentProvider, newProvider, action, services):
        # if name is None or newProvider is None or action is None:
        #    raise AttributeError("PIC given null attributes")
        self.name = name
        self.action = action
        if currentProvider is not None:
            self.currentProvider = Provider(risqueString=currentProvider)
        if newProvider is not None:
            self.newProvider = Provider(risqueString=newProvider)
        self.services = services
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

    def getProvider(self):
        if self.action == "Activate":
            if self.newProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return self.newProvider
        if self.action == "Modify":
            if self.newProvider is None and self.currentProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return (self.currentProvider, self.newProvider)[self.currentProvider is None]
        if self.action == "Deactivate":
            if self.newProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return self.newProvider

    def getConfig(self):

