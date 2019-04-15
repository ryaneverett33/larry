from ConfigurationDriver import ConfigurationDriver
from IOS import IOS
from Vlan import Vlan
from Speed import Speed
from Verify import Verify
from Logger import Logger


class Config:
    ticket = None
    verify = None
    hostChanged = False
    logger = None

    def __init__(self, ticket):
        self.ticket = ticket
        self.verify = Verify(ticket)
        self.logger = Logger.getInstance(ticket.number)

    def __basicDeactivate(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findFexInterface(pic, provider)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logBefore(pic.name, interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            # print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)
            self.logger.logWarning("DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider), True)

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
            interface = iosConnection.findFexInterface(pic, provider)
        else:
            interface = provider.getSwitchInterface()
        risqueConfig = pic.getConfig()

        switchConfig = iosConnection.getConfig(interface, flatten=False)
        upsCount = 0
        upsDevice = None
        self.logger.logBefore(pic.name, interface, switchConfig)
        switchGlobalVoiceVlan = iosConnection.findVoiceVlan()

        if provider.uplink:
            # print "Provider is an uplink port, not supported yet!"
            self.logger.logError("Provider is an uplink port, not supported yet!", True)
            return
        if pic.isUPS():
            upsCount = iosConnection.getUPSCount()
            upsDevice = provider.getUPSTypeFromProvider(provider)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        if iosConnection.isInterfaceEmpty(switchConfig):
            # Apply base config
            iosConnection.applyBaseTemplate(iosConnection.getBaseTemplate())

        # Set Description
        if pic.isUPS():
            # 70136
            # stew-215a-apc1500rm-01
            fixedUPSCount = "0{0}".format(upsCount + 1) if (upsCount + 1) < 10 else str(upsCount + 1) # add leading zeroes
            newDescription = "{0}-{1}-{2}-{3}".format(provider.building, provider.TR, upsDevice, fixedUPSCount)
            iosConnection.setDescription(newDescription)
        else:
            iosConnection.setDescription(pic.getDescription())
        # Set access mode
        iosConnection.setSwitchportMode("access")
        # Set speed
        if pic.isAP():
            if "Gi" in provider.intType:
                iosConnection.setSpeed(risqueConfig.speed)
                # set duplex
                iosConnection.setDuplex(Speed.DUPLEX_FULL)
            elif "Te" in provider.intType or "Tw" in provider.intType:
                iosConnection.setSpeed(Speed.SpeedAutoObject())
            else:
                iosConnection.setSpeed(risqueConfig.speed)
        else:
            iosConnection.setSpeed(risqueConfig.speed)
        # Set vlan
        iosConnection.setVlan(risqueConfig.vlan)
        # Set voice vlan
        if risqueConfig.voiceVlan is not None:
            iosConnection.setVoiceVlan(risqueConfig.voiceVlan)
        else:
            self.logger.logWarning("Risque does not have a voice vlan for {0}".format(pic.name), True)
            if switchGlobalVoiceVlan is None:
                self.logger.logError("Unable to retrieve voice vlan for switch", False)
            else:
                iosConnection.setVoiceVlan(switchGlobalVoiceVlan)
                self.logger.logInfo("Set voice vlan for {0} to {1}".format(pic.name, switchGlobalVoiceVlan), False)
        # set power for AP
        if pic.isAP() and "3750" in provider.switchType:
            iosConnection.setPower(20000)
        # Set no shut
        iosConnection.shutdown(no=True)

        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()
        self.hostChanged = True

    def __basicModify(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findFexInterface(pic, provider)
        else:
            interface = provider.getSwitchInterface()
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logBefore(pic.name, interface, switchConfig)
        vlan = iosConnection.getVlan(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        shutdown = iosConnection.isShutdown(interface, switchConfig)
        if not pic.isUPS and (description is None or description != pic.getDescription()):
            # print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)
            self.logger.logWarning("DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider), True)

        iosConnection.enterConfigMode()
        iosConnection.enterInterfaceConfig(interface)

        if vlan is None or vlan.tag != risqueConfig.vlan.tag:
            iosConnection.setVlan(risqueConfig.vlan)
            self.hostChanged = True
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                iosConnection.setVoiceVlan(risqueConfig.voiceVlan)
                self.hostChanged = True
        else:
            self.logger.logWarning("Risque does not have a voice vlan for {0}".format(pic.name), True)
            switchGlobalVoiceVlan = iosConnection.findVoiceVlan()
            if switchGlobalVoiceVlan is None:
                self.logger.logError("Unable to retrieve voice vlan for switch", False)
            # If voice vlan already exists on switch, ignore and continue
            # else add globalvoicevlan to interface
            if voiceVlan is None and switchGlobalVoiceVlan is not None:
                iosConnection.setVoiceVlan(switchGlobalVoiceVlan)
                self.logger.logInfo("Set voice vlan for {0} to {1}".format(pic.name, switchGlobalVoiceVlan), False)
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            iosConnection.setSpeed(risqueConfig.speed)
            self.hostChanged = True
        if shutdown:
            self.logger.logWarning("INTERFACE IS SHUTDOWN ON A MODIFY, ENABLING THE PORT - PIC: {0}, provider: {1}".format(pic.name, provider), True)
            iosConnection.shutdown(no=True)
            self.hostChanged = True
        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()

    def __trunkModify(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        if iosConnection.isFexHost:
            # print "Can't modify trunk port on a FEX host"
            self.logger.logError("Can't modify trunk port on a FEX host")
            return False
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logBefore(pic.name, interface, switchConfig)
        switchMode = iosConnection.getSwitchportMode(interface, switchConfig)
        nativeVlan = iosConnection.getNativeVlan(interface, switchConfig)
        taggedVlans = iosConnection.getTaggedVlans(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        shutdown = iosConnection.isShutdown(interface, switchConfig)
        if description is None or description != pic.getDescription():
            # print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)
            self.logger.logWarning(
                "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider), True)

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

        if shutdown:
            self.logger.logWarning("INTERFACE IS SHUTDOWN ON A MODIFY, ENABLING THE TRUNK PORT - PIC: {0}, provider: {1}".format(pic.name, provider), True)
            iosConnection.shutdown(no=True)
            self.hostChanged = True

        iosConnection.leaveInterfaceConfig()
        iosConnection.leaveConfigMode()

    def __trunkActivate(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        if iosConnection.isFexHost:
            # print "Can't modify trunk port on a FEX host"
            self.logger.logError("Can't modify trunk port on a FEX host")
            return False
        risqueConfig = pic.getConfig()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logBefore(pic.name, interface, switchConfig)
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
        if iosConnection.isFexHost:
            # print "Can't modify trunk port on a FEX host"
            self.logger.logError("Can't modify trunk port on a FEX host")
            return False
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logBefore(pic.name, interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        if description is None or description != pic.getDescription():
            self.logger.logError("Can't modify trunk port on a FEX host")
            # print "DESCRIPTIONS DON'T MATCH ON MODIFY - PIC: {0}, provider: {1}".format(pic.name, provider)

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
        elif pic.action == "Repair":
            self.logger.logError("PIC ({0},{1}) action is a Repair, cannot repair PICs".format(pic.name, provider), True)
            return
        if not self.verify.verify(iosConnection, provider, pic):
            self.logger.logError("Failed to configure {0} on {1}".format(pic.name, provider), True)
            # print "Failed to configure {0} on {1}".format(pic.name, provider)
        else:
            self.logger.logSuccess("Successfully configured {0}".format(pic.name), True)

    def run(self):
        currentHost = None
        iosConnection = None

        if len(self.ticket.configurablePics) == 0:
            # print Logger.WARNING + "Ticket has no configurable PICs, add provider ports to continue" + Logger.NORMAL
            self.logger.logWarning("Ticket has no configurable PICs, add provider ports to continue")
            return

        for pic in self.ticket.configurablePics:
            provider = pic.getProvider()
            newHost = provider.getHostFromProvider(provider)
            if provider.getHostFromProvider(provider) is None:
                # print Logger.FAIL + "Failed to get host for provider {0}".format(provider) + Logger.NORMAL
                self.logger.logError("Failed to get host for provider {0}".format(provider), True)
                continue
            if currentHost != newHost:
                if iosConnection is not None:
                    # leaving host
                    if self.hostChanged:
                        iosConnection.write()
                currentHost = newHost
                driver = ConfigurationDriver.getDriver()
                iosConnection = IOS(driver, currentHost, provider.switchType)
                self.hostChanged = False
            try:
                self.config(iosConnection, provider, pic)
            except Exception, e:
                # print "Failed to configure {0} with provider {1}, error: {2}".format(pic.name, provider, e)
                self.logger.logException("Failed to configure {0} with provider {1}".format(pic.name, provider), e, True)
        if iosConnection is not None:
            # leaving host
            if self.hostChanged:
                iosConnection.write()
