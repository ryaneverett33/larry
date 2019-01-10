from ConfigurationDriver import ConfigurationDriver
from IOS import IOS

class Verify:
    ticket = None

    def __init__(self, ticket):
        self.ticket = ticket

    def __verifyBasicDeactivate(self, switchConfig, pic):
        passed = True
        # Check shut status
        if "shut" not in switchConfig:
            print "{0} - Deactivated port has not been shutdown".format(pic.name)
            passed = False
        # Check vlan status
        if "switchport access vlan" in switchConfig:
            print "{0} - Deactivated port still has a vlan".format(pic.name)
            passed = False
        # Check speed
        if "speed" in switchConfig:
            print "{0} - Deactivated port still has a speed".format(pic.name)
            passed = False
        return passed

    def __verifyBasicActivate(self, risqueConfig, switchConfig, pic):
        print "Basic Activate not implemented yet"
        return False

    def __verifyBasicModify(self, risqueConfig, switchConfig, pic):
        print "Basic Modify not implemented yet"
        return False

    # Returns true/false if pic is correct, prints out any errors
    def __verify(self, risqueConfig, switchConfig, pic):
        if switchConfig is None:
            print "Failed to get switch config for {0}".format(pic.name)
            return False
        if pic.action == "Deactivate":
            return self.__verifyBasicDeactivate(switchConfig, pic)
        elif pic.action == "Activate":
            return self.__verifyBasicActivate(risqueConfig, switchConfig, pic)
        elif pic.action == "Modify":
            return self.__verifyBasicModify(risqueConfig, switchConfig, pic)
        else:
            print "PIC has invalid action, can't verify"
            return False

    def run(self):
        currentHost = None
        driver = None
        iosConnection = None
        failed = list()     # list of pics that are not valid
        for pic in self.ticket.pics:
            provider = pic.getProvider()
            if currentHost != provider.getHostFromProvider(provider):
                currentHost = provider.getHostFromProvider(provider)
                driver = ConfigurationDriver.getDriver().connect(currentHost)
                iosConnection = IOS(driver, currentHost, provider.switchType)
            # Get Config for provider
            risqueConfig = pic.getConfig()
            switchConfig = iosConnection.getConfig(provider.getSwitchInterface())
            if not self.__verify(risqueConfig, switchConfig, pic):
                failed.append(pic)
        if len(failed) != 0:
            print "The following PICs are invalid"
            for pic in failed:
                print "\t" + pic.name
        else:
            print "All PICs are valid"
