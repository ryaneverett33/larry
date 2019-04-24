from Speed import Speed
from Vlan import Vlan
from Provider import Provider
from Patch import Patch
from Services import Services
import re


class PICConfig:
    voiceVlan = None
    vlan = None     # Can be an array [Native vlan or access vlan]
    taggedVlans = None
    vlanList = False
    speed = None
    trunk = False
    services = None

    def __init__(self, vlan, speed):
        if type(speed) is not str or vlan is None:
            raise AttributeError("PICConfig given null attributes")
        if type(vlan) is str:
            self.vlan = Vlan(risqueString=vlan)
            self.vlanList = False
        elif isinstance(vlan, list):
            self.trunk = True
            self.vlan = []
            for v in vlan:
                self.vlan.append(Vlan(risqueString=v))
            self.vlanList = True
        self.speed = Speed(risqueString=speed)

    def addVoiceVlan(self, voiceVlan):
        if isinstance(voiceVlan, Vlan):
            self.voiceVlan = voiceVlan
            return
        if type(voiceVlan) is not str:
            raise AttributeError("addVoiceVlan given null attributes")
        self.voiceVlan = Vlan(risqueString=voiceVlan)

    def addTaggedVlans(self, taggedVlans):
        if not isinstance(taggedVlans, list):
            raise AttributeError("addTaggedVlans given null attributes")
        self.taggedVlans = list()
        for vlan in taggedVlans:
            self.taggedVlans.append(Vlan(risqueString=vlan))
        self.trunk = True

    def addServices(self, services):
        if not isinstance(services, list):
            raise AttributeError("addServices given null attributes")
        self.services = Services(services)

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
    trunk = False
    patch = None
    apRegex = re.compile("(AP-)[A-z]+")
    upsRegex = re.compile("[A-z-0-9]+(HW-UPS)")

    def __init__(self, name, currentProvider, newProvider, action, services):
        # if name is None or newProvider is None or action is None:
        #    raise AttributeError("PIC given null attributes")
        self.name = name
        self.action = action
        if currentProvider is not None:
            try:
                self.currentProvider = Provider(risqueString=currentProvider)
            except:
                self.currentProvider = None
        if newProvider is not None:
            try:
                self.newProvider = Provider(risqueString=newProvider)
            except:
                print "Failed to parse newProvider"
                self.newProvider = None
        self.services = services
        self.__isValidAction()

    def applyCurrentConfig(self, voiceVlan, vlan, speed):
        if vlan is None and speed is None:
            raise AttributeError("Invalid Config, must have a vlan and a speed")
        self.currentConfig = PICConfig(vlan, speed)
        if voiceVlan is not None:
            self.currentConfig.addVoiceVlan(voiceVlan)
        if self.currentConfig.trunk:
            self.trunk = True

    def applyNewConfig(self, voiceVlan, vlan, speed):
        if vlan is None and speed is None:
            raise AttributeError("Invalid Config, must have a vlan and a speed")
        self.newConfig = PICConfig(vlan, speed)
        if voiceVlan is not None:
            self.newConfig.addVoiceVlan(voiceVlan)
        else:
            # voice vlan is None
            if self.currentConfig is not None and self.currentConfig.voiceVlan is not None:
                print "New config doesn't have a voice vlan but current config does, using old voice vlan"
                self.newConfig.addVoiceVlan(self.currentConfig.voiceVlan)

    def __isValidAction(self):
        if self.action == "Activate":
            return
        elif self.action == "Deactivate":
            return
        elif self.action == "Modify":
            return
        elif self.action == "Repair":
            return
        else:
            raise ValueError("PIC given an invalid action")

    def addTaggedVlans(self, vlans):
        if vlans is None:
            raise AttributeError("Invalid tagged vlans - null")
        self.newConfig.addTaggedVlans(vlans)
        self.trunk = True

    def addServices(self, new, services):
        if services is None:
            raise AttributeError("Invalid tagged vlans - null")
        if new:
            self.newConfig.addServices(services)
        else:
            self.currentConfig.addServices(services)

    def getProvider(self):
        if self.action == "Activate":
            if self.newProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return self.newProvider
        elif self.action == "Modify":
            if self.newProvider is None and self.currentProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return (self.newProvider, self.currentProvider)[self.currentProvider is None]
        elif self.action == "Deactivate":
            if self.newProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return self.newProvider
        elif self.action == "Repair":
            if self.newProvider is None:
                raise AttributeError("Provider hasn't been supplied yet")
            return self.newProvider

    def getConfig(self):
        if self.action == "Activate":
            if self.newConfig is None:
                raise AttributeError("Config hasn't been supplied yet")
            return self.newConfig
        elif self.action == "Modify":
            return self.newConfig
        elif self.action == "Deactivate":
            if self.newConfig is None:
                raise AttributeError("Config hasn't been supplied yet")
            return self.newConfig
        elif self.action == "Repair":
            if self.newConfig is not None:
                return self.newConfig
            elif self.currentConfig is not None:
                return self.currentConfig
            else:
                raise AttributeError("Config hasn't been supplied yet")

    def addPatchPanel(self, patchString):
        try:
            self.patch = Patch(risqueString=patchString)
        except:
            # if we fail to add parse the patch panel, silently fail
            self.patch = None

    def getDescription(self):
        return self.name.lower()

    def isAP(self):
        # matches PICs of type BIDC-103AP-B but not of type BIDC-103A-AP
        if self.apRegex.match(self.name) is not None:
            return True
        # check if vlan is 1001, see #70004 for an AP THAT DOESN'T FOLLOW THE STANDARD
        config = self.getConfig()
        if config is None:
            return False
        if isinstance(config.vlan, Vlan) and config.vlan.tag == 1001:
            return True
        return False

    def isUPS(self):
        # matches PICs of type CREC-B318HW-UPS
        return self.upsRegex.match(self.name) is not None

    def getUPSName(self):
        # return name of type yong-664-trp1500
        provider = self.getProvider()

