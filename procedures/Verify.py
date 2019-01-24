from ConfigurationDriver import ConfigurationDriver
from IOS import IOS
from Vlan import Vlan
import traceback

class Verify:
    ticket = None

    def __init__(self, ticket):
        self.ticket = ticket

    # Issue handling deactivate for trunk ports
    def __verifyBasicDeactivate(self, iosConnection, provider, pic):
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findInterfaceOfPic(pic.name)
            print "Fex port has interface {0}".format(interface)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface)
        if switchConfig is None:
            print "{0} - Failed to get config".format(pic.name)
            return False
        passed = True
        # Check shut status
        if "shut" not in switchConfig:
            print "{0} - port has not been shutdown".format(pic.name)
            passed = False
        # Check vlan status
        if "switchport access vlan" in switchConfig:
            print "{0} - port still has a vlan".format(pic.name)
            passed = False
        # Check speed
        if "speed" in switchConfig:
            print "{0} - port still has a speed".format(pic.name)
            passed = False
        return passed

    def __verifyBasicWork(self, iosConnection, provider, pic):
        passed = True
        interface = None
        if iosConnection.isFexHost:
            interface = iosConnection.findInterfaceOfPic(pic.name)
            print "Fex port has interface {0}".format(interface)
        else:
            interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        if switchConfig is None:
            print "{0} - Failed to get config".format(pic.name)
            return False
        risqueConfig = pic.getConfig()

        # Check empty
        if iosConnection.isInterfaceEmpty(switchConfig):
            print "{0} - port isn't fully configured".format(pic.name)
            passed = False

        # Check shut status
        if iosConnection.isShutdown(interface, switchConfig):
            print "{0} - port is shutdown".format(pic.name)
            passed = False
        speed = iosConnection.getSpeed(interface, switchConfig)
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        mode = iosConnection.getSwitchportMode(interface, switchConfig)
        vlan = iosConnection.getVlan(interface, switchConfig)
        # Check speed
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            print "{0} - incorrect speed".format(pic.name)
            print "\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed)
            passed = False
        # Check voice
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                print "{0} - incorrect voice vlan".format(pic.name)
                print "\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan)
                passed = False
        # Check description
        if description != pic.getDescription():
            print "{0} - incorrect description".format(pic.name)
            print "\trisque: {0}, switch: {1}".format(pic.getDescription(), description)
            passed = False
        # Check mode
        if mode != "access":
            print "{0} - switchport is not set to access mode".format(pic.name)
            passed = False
        # Check vlan
        if vlan is None or vlan.tag != risqueConfig.vlan.tag:
            print "{0} - incorrect vlan".format(pic.name)
            print "\trisque: {0}, switch: {1}".format(risqueConfig.vlan, vlan)
            passed = False
        return passed

    def __verifyTrunkDeactivate(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface)
        if switchConfig is None:
            print "{0} - Failed to get config".format(pic.name)
            return False
        passed = True
        # Check shut status
        if "shut" not in switchConfig:
            print "{0} - port has not been shutdown".format(pic.name)
            passed = False
        # Check native vlan status
        if "switchport trunk native vlan" in switchConfig:
            print "{0} - port still has a native vlan".format(pic.name)
            passed = False
        # Check tagged vlans only 1
        if "switchport trunk allowed vlan 1" not in switchConfig:
            print "{0} - port still has a native vlan".format(pic.name)
            passed = False
        # Check speed
        if "speed" in switchConfig:
            print "{0} - port still has a speed".format(pic.name)
            passed = False
        return passed

    def __verifyTrunkWork(self, iosConnection, provider, pic):
        interface = provider.getSwitchInterface()
        switchConfig = iosConnection.getConfig(interface, flatten=False)
        risqueConfig = pic.getConfig()
        if switchConfig is None:
            print "{0} - Failed to get config".format(pic.name)
            return False
        passed = True
        voiceVlan = iosConnection.getVoiceVlan(interface, switchConfig)
        description = iosConnection.getDescription(interface, switchConfig)
        mode = iosConnection.getSwitchportMode(interface, switchConfig)
        speed = iosConnection.getSpeed(interface, switchConfig)
        # Check speed
        if speed is None or speed.speedTuple != risqueConfig.speed.speedTuple:
            print "{0} - incorrect speed".format(pic.name)
            print "\trisque: {0}, switch: {1}".format(risqueConfig.speed, speed)
            passed = False
        # Check shut status
        if iosConnection.isShutdown(interface, switchConfig):
            print "{0} - port is shutdown".format(pic.name)
            passed = False
        # Check voice
        if risqueConfig.voiceVlan is not None:
            if voiceVlan is None or voiceVlan.tag != risqueConfig.voiceVlan.tag:
                print "{0} - incorrect voice vlan".format(pic.name)
                print "\trisque: {0}, switch: {1}".format(risqueConfig.voiceVlan, voiceVlan)
                passed = False
        nativeVlan = iosConnection.getNativeVlan(interface, switchConfig)
        taggedVlans = iosConnection.getTaggedVlans(interface, switchConfig)
        # Check mode
        if mode != "trunk":
            print "{0} - switchport is not set to trunk mode".format(pic.name)
            passed = False
        # Check the native vlan (IT MAY NOT EXIST)
        if risqueConfig.vlan is not None and risqueConfig.vlan.tag != 1:
            if nativeVlan is None or nativeVlan.tag != risqueConfig.vlan.tag:
                print "{0} - incorrect native vlan".format(pic.name)
                print "\trisque: {0}, switch: {1}".format(risqueConfig.vlan, nativeVlan)
                passed = False
        # Check tagged vlans
        for vlan in risqueConfig.taggedVlans:
            if vlan is None or not Vlan.tagInVlanList(taggedVlans, vlan.tag):
                print "{0} missing tagged vlan {1}".format(pic.name, vlan)
                passed = False
        return passed

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
        else:
            print "PIC has invalid action, can't verify"
            return False

    def run(self):
        currentHost = None
        iosConnection = None
        failed = list()     # list of pics that are not valid
        for pic in self.ticket.pics:
            provider = pic.getProvider()
            if provider.getHostFromProvider(provider) is None:
                print "Failed to get host for provider {0}".format(provider)
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
            except Exception, e:
                traceback.print_exc()
                print "Failed to verify {0} with provider {1}, error: {2}".format(pic.name, provider, e)

        if len(failed) != 0:
            print "The following PICs are invalid"
            for pic in failed:
                print "\t" + pic.name
        else:
            print "All PICs are valid"
