from ConfigurationDriver import ConfigurationDriver
from IOS import IOS
from Vlan import Vlan
from Speed import Speed
from Verify import Verify


class Config:
    ticket = None
    verify = None
    hostChanged = False

    def __init__(self, ticket):
        self.ticket = ticket
        self.verify = Verify(ticket)

    def __basicDeactivate(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findInterfaceOfPic(pic.name)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        # Shutdown port
        iosConnection.shutdown()
        # Switchport access vlan 1
        iosConnection.setVlan(Vlan.Vlan1())
        # no speed
        iosConnection.setSpeed(Speed.NoSpeed())
        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()
        self.hostChanged = True

    def __basicActivate(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findInterfaceOfPic(pic.name)
        else:
            interface = provider.getSwitchInterface()
        risqueConfig = pic.getConfig()

        switchConfig = iosConnection.getConfig(interface, flatten=False)

        if provider.uplink:
            print "Provider is an uplink port, not supported yet!"
            return

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        if iosConnection.isInterfaceEmpty(switchConfig):
            # Apply base config
            iosConnection.applyBaseTemplate(iosConnection.getBaseTemplate())

        # Set Description
        iosConnection.setDescription(pic.getDescription())
        # Set access mode
        iosConnection.setSwitchportMode("access")
        # Set speed
        iosConnection.setSpeed(risqueConfig.speed)
        # Set vlan
        iosConnection.setVlan(risqueConfig.vlan)
        # Set voice vlan
        if risqueConfig.voiceVlan is not None:
            iosConnection.setVoiceVlan(risqueConfig.voiceVlan)
        # Set no shut
        iosConnection.shutdown(no=True)

        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()
        self.hostChanged = True

    def __basicModify(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findInterfaceOfPic(pic.name)
        else:
            interface = provider.getSwitchInterface()
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        vlan = iosConnection.getVlan(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        if vlan is None or vlan.tag != risqueConfig.vlan.tag:
            iosConnection.setVlan(risqueConfig.vlan)
            self.hostChanged = True
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                iosConnection.setVoiceVlan(risqueConfig.voiceVlan)
                self.hostChanged = True
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            iosConnection.setSpeed(risqueConfig.speed)
            self.hostChanged = True
        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()

    def __trunkModify(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        if iosConnection.isFexHost:
            print "Can't modify trunk port on a FEX host"
            return False
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        switchMode = iosConnection.getSwitchportMode(interface, switchConfig)
        nativeVlan = iosConnection.getNativeVlan(interface, switchConfig)
        taggedVlans = iosConnection.getTaggedVlans(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)
        if switchMode is None or switchMode != "trunk":
            iosConnection.setSwitchportMode("trunk")
            self.hostChanged = True
        if nativeVlan is None and risqueConfig.vlan.tag != 1 or nativeVlan.tag != risqueConfig.vlan.tag:
            iosConnection.setNativeVlan(risqueConfig.vlan)
            self.hostChanged = True
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            iosConnection.setSpeed(risqueConfig.speed)
            self.hostChanged = True
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                iosConnection.setVoiceVlan(risqueConfig.voiceVlan)
                self.hostChanged = True
        # if switchport trunk tagged vlans is absent, set Tagged Vlans
        # else, add tagged vlans that don't exist on switch already
        if taggedVlans is None:
            iosConnection.setTaggedVlans(risqueConfig.taggedVlans)
            self.hostChanged = True
        else:
            vlans = list()
            for vlan in risqueConfig.taggedVlans:
                found = False
                for vlan2 in taggedVlans:
                    if vlan2.tag == vlan.tag:
                        found = True
                        break
                if not found:
                    vlans.append(vlan)
            if len(vlans) > 0:
                iosConnection.addTaggedVlans(vlans)
                self.hostChanged = True

        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()

    def __trunkActivate(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        if iosConnection.isFexHost:
            print "Can't modify trunk port on a FEX host"
            return False
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        switchMode = iosConnection.getSwitchportMode(interface, switchConfig)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)
        if switchMode is None or switchMode != "trunk":
            iosConnection.setSwitchportMode("trunk")
            self.hostChanged = True
        iosConnection.setNativeVlan(risqueConfig.vlan)
        iosConnection.setTaggedVlans(risqueConfig.taggedVlans)
        iosConnection.setSpeed(risqueConfig.speed)
        iosConnection.shutdown(no=True)
        iosConnection.setDescription(pic.getDescription())

        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()

    def __trunkDeactivate(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        # Shutdown port
        iosConnection.shutdown()
        # Switchport trunk allowed vlan 1
        iosConnection.setTaggedVlans(Vlan.Vlan1())
        iosConnection.setNativeVlan(Vlan.Vlan1())
        # no speed
        iosConnection.setSpeed(Speed.NoSpeed())
        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()
        self.hostChanged = True

    def config(self, iosConnection, provider, pic):
        if pic.action == "Deactivate":
            if pic.trunk:
                self.__trunkDeactivate(iosConnection, provider, pic)
            else:
                self.__basicDeactivate(iosConnection, provider, pic)
        elif pic.action == "Activate":
            if pic.trunk:
                self.__trunkActivate(iosConnection, provider, pic)
            else:
                self.__basicActivate(iosConnection, provider, pic)
        elif pic.action == "Modify":
            if pic.trunk:
                self.__trunkModify(iosConnection, provider, pic)
            else:
                self.__basicModify(iosConnection, provider, pic)
        if not self.verify.verify(iosConnection, provider, pic):
            print "Failed to configure {0} on {1}".format(pic.name, provider)
            print "Switch configuration"
            print iosConnection.getConfig(provider.getSwitchInterface(), flatten=False)

    def run(self):
        currentHost = None
        iosConnection = None
        for pic in self.ticket.pics:
            provider = pic.getProvider()
            newHost = provider.getHostFromProvider(provider)
            if currentHost != newHost:
                if iosConnection is not None:
                    # leaving host
                    if self.hostChanged:
                        iosConnection.write()
                currentHost = newHost
                driver = ConfigurationDriver.getDriver()
                iosConnection = IOS(driver, currentHost, provider.switchType)
                self.hostChanged = False
            try :
                self.config(iosConnection, provider, pic)
            except Exception, e:
                print "Failed to configure {0} with provider {1}, error: {2}".format(pic.name, provider, e)
        if iosConnection is not None:
            # leaving host
            if self.hostChanged:
                iosConnection.write()
