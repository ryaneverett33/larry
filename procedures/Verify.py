from ConfigurationDriver import ConfigurationDriver
from IOS import IOS
from Vlan import Vlan
import traceback
from Logger import Logger


class Verify:
    ticket = None
    logger = None

    def __init__(self, ticket):
        self.ticket = ticket
        self.logger = Logger.getInstance(ticket.number)

    # Issue handling deactivate for trunk ports
    def __verifyBasicDeactivate(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findFexInterface(pic, provider)
            # print "Fex port has interface {0}".format(interface)
            self.logger.logInfo("Fex port has interface {0}".format(interface), True)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface)
        self.logger.logAfter(pic.name, interface, switchConfig)
        if switchConfig is None:
            # print "{0} - Failed to get config".format(pic.name)
            self.logger.logError("{0} - Failed to get config".format(pic.name), True)
            return False
        passed = True
        # Check shut status
        if "shut" not in switchConfig:
            # print "{0} - port has not been shutdown".format(pic.name)
            self.logger.logError("{0} - port has not been shutdown".format(pic.name), True)
            passed = False
        # Check vlan status
        if "switchport access vlan" in switchConfig:
            # print "{0} - port still has a vlan".format(pic.name)
            self.logger.logError("{0} - port still has a vlan".format(pic.name), True)
            passed = False
        # Check speed
        if "speed" in switchConfig:
            # print "{0} - port still has a speed".format(pic.name)
            self.logger.logError("{0} - port still has a speed".format(pic.name), True)
            passed = False
        return passed

    def __verifyBasicWork(self, iosConnection, provider, pic):
        passed = True
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findFexInterface(pic, provider)
            # print "Fex port has interface {0}".format(interface)
            self.logger.logInfo("Fex port has interface {0}".format(interface), False)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logAfter(pic.name, interface, switchConfig)
        if switchConfig is None:
            # print "{0} - Failed to get config".format(pic.name)
            self.logger.logError("{0} - Failed to get config".format(pic.name), True)
            return False
        risqueConfig = pic.getConfig()

        # Check empty
        if iosConnection.isInterfaceEmpty(switchConfig):
            # print "{0} - port isn't fully configured".format(pic.name)
            self.logger.logError("{0} - port isn't fully configured".format(pic.name), True)
            passed = False

        # Check shut status
        if iosConnection.isShutdown(interface, switchConfig):
            # print "{0} - port is shutdown".format(pic.name)
            self.logger.logError("{0} - port is shutdown".format(pic.name), True)
            passed = False
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        mode = iosConnection.getSwitchportMode(interface, switchConfig)
        vlan = iosConnection.getVlan(interface, switchConfig)
        # Check speed
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            # print "{0} - incorrect speed".format(pic.name)
            # print "\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed)
            self.logger.logError("{0} - incorrect speed".format(pic.name), True)
            self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed), True)
            passed = False
        # Check voice
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                # print "{0} - incorrect voice vlan".format(pic.name)
                # print "\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan)
                self.logger.logError("{0} - incorrect voice vlan".format(pic.name), True)
                self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan), True)
                passed = False
        else:
            self.logger.logWarning("Risque doesn't have a voice vlan", True)
            switchGlobalVoiceVlan = iosConnection.findVoiceVlan()
            if voiceVlan is None:
                if switchGlobalVoiceVlan is not None:
                    self.logger.logError("{0} does not have a voice vlan".format(pic.name), True)
                    passed = False
            else:
                # self.logger.logInfo("{0} has voice vlan {1}".format(pic.name, voiceVlan), True)
                # check if globalvoicevlan and current voice vlan are the same
                if switchGlobalVoiceVlan == str(voiceVlan.tag):
                    self.logger.logInfo("Voice vlan for {0} is {1}".format(pic.name, switchGlobalVoiceVlan), True)
                else:
                    self.logger.logWarning("{0} has a different voice vlan ({1}) than the switch's 'global' voice vlan({2})"
                                           .format(pic.name, voiceVlan.tag, switchGlobalVoiceVlan), True)
        # Check description
        if description != pic.getDescription():
            # print "{0} - incorrect description".format(pic.name)
            # print "\trisque: {0}, switch: {1}".format(pic.getDescription(), description)
            self.logger.logError("{0} - incorrect description".format(pic.name), True)
            self.logger.logError("\trisque: {0}, switch: {1}".format(pic.getDescription(), description), True)
            passed = False
        # Check mode
        if mode != "access":
            # print "{0} - switchport is not set to access mode".format(pic.name)
            self.logger.logError("{0} - switchport is not set to access mode".format(pic.name), True)
            passed = False
        # Check vlan
        if vlan is None or vlan.tag != risqueConfig.vlan.tag:
            # print "{0} - incorrect vlan".format(pic.name)
            # print "\trisque: {0}, switch: {1}".format(risqueConfig.vlan, vlan)
            self.logger.logError("{0} - incorrect vlan".format(pic.name), True)
            self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.vlan, vlan), True)
            passed = False
        return passed

    def __verifyTrunkDeactivate(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface)
        self.logger.logAfter(pic.name, interface, switchConfig)
        if switchConfig is None:
            # print "{0} - Failed to get config".format(pic.name)
            self.logger.logError("{0} - Failed to get config".format(pic.name), True)
            return False
        passed = True
        # Check shut status
        if "shut" not in switchConfig:
            # print "{0} - port has not been shutdown".format(pic.name)
            self.logger.logError("{0} - port has not been shutdown".format(pic.name), True)
            passed = False
        # Check native vlan status
        if "switchport trunk native vlan" in switchConfig:
            # print "{0} - port still has a native vlan".format(pic.name)
            self.logger.logError("{0} - port still has a native vlan".format(pic.name), True)
            passed = False
        # Check tagged vlans only 1
        if "switchport trunk allowed vlan 1" not in switchConfig:
            # print "{0} - port still has a native vlan".format(pic.name)
            self.logger.logError("{0} - port still has tagged vlans".format(pic.name), True)
            passed = False
        # Check speed
        if "speed" in switchConfig:
            # print "{0} - port still has a speed".format(pic.name)
            self.logger.logError("{0} - port still has a speed".format(pic.name), True)
            passed = False
        return passed

    def __verifyTrunkWork(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        self.logger.logAfter(pic.name, interface, switchConfig)
        risqueConfig = pic.getConfig()
        if switchConfig is None:
            # print "{0} - Failed to get config".format(pic.name)
            self.logger.logError("{0} - Failed to get config".format(pic.name), True)
            return False
        passed = True
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        mode = iosConnection.getSwitchportMode(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        # Check speed
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            # print "{0} - incorrect speed".format(pic.name)
            # print "\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed)
            self.logger.logError("{0} - incorrect speed".format(pic.name), True)
            self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed), True)
            passed = False
        # Check shut status
        if iosConnection.isShutdown(interface, switchConfig):
            # print "{0} - port is shutdown".format(pic.name)
            self.logger.logError("{0} - port is shutdown".format(pic.name), True)
            passed = False
        # Check voice
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                # print "{0} - incorrect voice vlan".format(pic.name)
                # print "\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan)
                self.logger.logError("{0} - incorrect voice vlan".format(pic.name), True)
                self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan), True)
                passed = False
        nativeVlan = iosConnection.getNativeVlan(interface, switchConfig)
        taggedVlans = iosConnection.getTaggedVlans(interface, switchConfig)
        # Check mode
        if mode != "trunk":
            # print "{0} - switchport is not set to trunk mode".format(pic.name)
            self.logger.logError("{0} - switchport is not set to trunk mode".format(pic.name), True)
            passed = False
        # Check the native vlan (IT MAY NOT EXIST)
        if risqueConfig.vlan is not None and risqueConfig.vlan.tag != 1:
            if nativeVlan is None or nativeVlan.tag != risqueConfig.vlan.tag:
                # print "{0} - incorrect native vlan".format(pic.name)
                # print "\trisque: {0}, switch: {1}".format(risqueConfig.vlan, nativeVlan)
                self.logger.logError("{0} - incorrect native vlan".format(pic.name), True)
                self.logger.logError("\trisque: {0}, switch: {1}".format(risqueConfig.vlan, nativeVlan), True)
                passed = False
        # Check tagged vlans
        for vlan in risqueConfig.taggedVlans:
            if vlan is None or not Vlan.tagInVlanList(taggedVlans, vlan.tag):
                # print "{0} missing tagged vlan {1}".format(pic.name, vlan)
                self.logger.logError("{0} missing tagged vlan {1}".format(pic.name, vlan), True)
                passed = False
        return passed

    def __verifyRepair(self, iosConnection, provider, pic):
        try:
            interface = provider.getSwitchInterface()
            connection = iosConnection.getConnectionState(interface)
            if connection != "connected":
                if connection == "disabled" or connection == "err-disabled":
                    self.logger.logError("{0} is down ({1})".format(pic.name, connection), True)
                elif connection == "notconnect":
                    self.logger.logWarning("{0} is down (notconnect)".format(pic.name), True)
                # check if there are mac addresses
                macAddresses = iosConnection.getMacAddresses(interface)
                if len(macAddresses) > 0:
                    self.logger.logInfo("{0} has {1} mac addresses connected to it".format(pic.name, len(macAddresses)), True)
                    return True
                else:
                    self.logger.logError("{0} has no mac addresses connected to it".format(pic.name), True)
                    return False
            else:
                return True
        except Exception, e:
            self.logger.logException("Exception occurred verifying repair", e, False)
            print "Failed to Verify repair, check logs for error"
            return False

    # Returns true/false if pic is correct, prints out any errors
    def verify(self, iosConnection, provider, pic):
        if pic.action == "Deactivate":
            if pic.trunk:
                return self.__verifyTrunkDeactivate(iosConnection, provider, pic)
            else:
                return self.__verifyBasicDeactivate(iosConnection, provider, pic)
        elif pic.action == "Activate":
            if pic.trunk:
                return self.__verifyTrunkWork(iosConnection, provider, pic)
            else:
                return self.__verifyBasicWork(iosConnection, provider, pic)
        elif pic.action == "Modify":
            if pic.trunk:
                return self.__verifyTrunkWork(iosConnection, provider, pic)
            else:
                return self.__verifyBasicWork(iosConnection, provider, pic)
        elif pic.action == "Repair":
            return self.__verifyRepair(iosConnection, provider, pic)
        else:
            self.logger.printError("PIC has invalid action, can't verify", True)
            # print "PIC has invalid action, can't verify"
            return False

    def printFailedPics(self, pics):
        self.logger.logError("Failed:", True)
        counter = 0
        string = ""
        for i in range(0, len(pics)):
            string = string + "{0}{1}".format((", ", "")[counter == 0], pics[i].name)
            counter = counter + 1
            if counter == 5:
                # print string
                self.logger.logError(string, True)
                counter = 0
                string = ""
        # flush out string
        if counter > 0:
            self.logger.logError(string, True)
            # print string

    def printSummary(self, pics, failed):
        if len(failed) == 0:
            # print Logger.OKGREEN + "{0}/{1} PASSED - 0/{1} FAILED".format(len(pics), len(pics)) + Logger.NORMAL
            self.logger.logSuccess("{0}/{1} PASSED - 0/{1} FAILED".format(len(pics), len(pics)), True)
        else:
            # print "{0} {1}/{2} PASSED - {3}/{2} FAILED".format((Logger.WARNING, Logger.FAIL)[len(failed) == len(pics)], len(pics) - len(failed), len(pics), len(failed)) + Logger.NORMAL
            coloredString = "{0} {1}/{2} PASSED - {3}/{2} FAILED".format((Logger.WARNING, Logger.FAIL)[len(failed) == len(pics)], len(pics) - len(failed), len(pics), len(failed)) + Logger.NORMAL
            string = "{0}/{1} PASSED - {2}/{1} FAILED".format(len(pics) - len(failed), len(pics), len(failed))
            self.logger.logInfo(string, False)
            if Logger.disableColor:
                print string
            else:
                print coloredString
            self.printFailedPics(failed)

    def run(self):
        currentHost = None
        iosConnection = None
        failed = list()     # list of pics that are not valid

        if len(self.ticket.configurablePics) == 0:
            # print Logger.WARNING + "Ticket has no configurable PICs, add provider ports to continue" + Logger.NORMAL
            self.logger.logWarning("Ticket has no configurable PICs, add provider ports to continue", True)
            return

        for pic in self.ticket.configurablePics:
            provider = pic.getProvider()
            if provider.getHostFromProvider(provider) is None:
                # print Logger.FAIL + "Failed to get host for provider {0}".format(provider) + Logger.NORMAL
                self.logger.logError("Failed to get host for provider {0}".format(provider), True)
                failed.append(pic)
                continue
            if currentHost != provider.getHostFromProvider(provider):
                currentHost = provider.getHostFromProvider(provider)
                driver = ConfigurationDriver.getDriver()
                if iosConnection is not None:
                    iosConnection.disconnect()
                iosConnection = IOS(driver, currentHost, provider.switchType)
            try:
                if not self.verify(iosConnection, provider, pic):
                    failed.append(pic)
                else:
                    # print Logger.OKGREEN + "{0} is valid".format(pic.name) + Logger.NORMAL
                    self.logger.logSuccess("{0} is valid".format(pic.name), True)
            except Exception, e:
                # traceback.print_exc()
                # print Logger.FAIL + "Failed to verify {0} with provider {1}, error: {2}".format(pic.name, provider, e) + Logger.NORMAL
                self.logger.logException("Failed to verify {0} with provider {1}".format(pic.name, provider), e, True)
                failed.append(pic)

        self.printSummary(self.ticket.configurablePics, failed)
        # if len(failed) != 0:
        #    print "The following PICs are invalid"
        #    self.printFailedPics(failed)
        # else:
        #    print Logger.OKGREEN + "All PICs are valid"
