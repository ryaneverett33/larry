from Vlan import Vlan
from Speed import Speed


# Represents an SSH connection to an IOS switch
class IOS:
    sshClient = None
    host = None
    switchType = None   # e.g. c3750ep

    def __init__(self, sshClient, host, switchType):
        self.sshClient = sshClient
        if self.sshClient.connected:
            self.sshClient.disconnect()
        self.sshClient.connect(host)
        self.switchType = switchType

    def sis(self):
        # [output, hostname]
        result = self.sshClient.execute('sis')

    def __isValidResponse(self, commandResponse):
        return (True, False)["Invalid input" in commandResponse]

    def __flatten(self, arr, char='\n'):
        string = ""
        for i in arr:
            string = string + i
            string = string + char
        return string

    # return an array of lines
    def getConfig(self, interface, flatten=True):
        switchConfig = self.sshClient.execute("show run int {0}".format(interface))[0]
        if not self.__isValidResponse(switchConfig):
            print "Failed to get switch config, {0} may be invalid".format(interface)
            return None
        # clean up lines
        lines = []
        rawLines = switchConfig.split('\n')
        for line in rawLines:
            if "Current configuration" in line:
                continue
            if "Building configuration" in line:
                continue
            if line == "!":
                continue
            if "interface" in line:
                continue
            if "end" in line:
                continue
            lines.append(line.strip())
        if flatten:
            return self.__flatten(lines)
        else:
            return lines

    def currentMode(self):
        a = None

    def getDescription(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "description" in line:
                return line.split(' ')[1]
        return None

    def getVlan(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "access vlan" in line:
                return Vlan(switchString=line)
        return Vlan.Vlan1()

    def getVoiceVlan(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "voice vlan" in line:
                return Vlan(switchString=line)
        return None

    def getSpeed(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "speed" in line:
                return Speed(switchString=line)
        return None

    def isShutdown(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "shut" in line:
                return True
        return False

    # Return "access" if switchport mode access, "trunk" if switchport mode trunk
    def getSwitchportMode(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "switchport mode" in line:
                if "trunk" in line:
                    return "trunk"
                elif "access" in line:
                    return "access"
                else:
                    print "Unknown switchport mode: {0}".format(line)
        return None

    def getTaggedVlans(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "switchport trunk allowed" in line:
                return Vlan(switchString=line)
        return None

    def getNativeVlan(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "switchport trunk native" in line:
                return Vlan(switchString=line)
        return None
