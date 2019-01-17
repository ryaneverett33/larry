from Vlan import Vlan
from Speed import Speed


# Represents an SSH connection to an IOS switch
class IOS:
    sshClient = None
    host = None
    switchType = None   # e.g. c3750ep
    inConfigMode = False
    inInterface = False

    def __init__(self, sshClient, host, switchType):
        self.sshClient = sshClient
        if self.sshClient.connected:
            self.sshClient.disconnect()
        self.sshClient.connect(host)
        self.switchType = switchType
        if self.sshClient.isForbiddenHost():
            raise NotImplementedError("Not allowed to make changes on host {0}, Reason: DISALLOWED_HOST".format(host))

    def sis(self):
        # [output, hostname]
        # result = self.sshClient.execute('sis')
        raise NotImplementedError()

    def disconnect(self):
        self.sshClient.disconnect()

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
        switchConfig = None
        if self.inConfigMode:
            print "IOS::getConfig() in Config Mode!!"
            switchConfig = self.sshClient.execute("do show run int {0}".format(interface))[0]
        else:
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
        raise NotImplementedError()

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

    def setVlan(self, newVlan, no=False):
        if not self.inConfigMode:
            print "can't set vlan when not in config mode"
            return False
        if not self.inInterface:
            print "can't set vlan when not configuring interface"
            return False
        result = None
        if no:
            result = self.sshClient.execute("no switchport access vlan {0}".format(newVlan.tag))[0]
        else:
            result = self.sshClient.execute("switchport access vlan {0}".format(newVlan.tag))[0]
        if not self.__isValidResponse(result):
            print "Failed to set vlan, vlan {0} may be bad".format(newVlan)
            return False
        return True

    def setVoiceVlan(self, newVoiceVlan, no=False):
        if not self.inConfigMode:
            print "can't set voice vlan when not in config mode"
            return False
        if not self.inInterface:
            print "can't set voice vlan when not configuring interface"
            return False
        result = None
        if no:
            result = self.sshClient.execute("no switchport voice vlan {0}".format(newVoiceVlan.tag))[0]
        else:
            result = self.sshClient.execute("switchport voice vlan {0}".format(newVoiceVlan.tag))[0]
        if not self.__isValidResponse(result):
            print "Failed to set voice vlan, vlan {0} may be bad".format(newVoiceVlan)
            return False
        return True

    def enterConfigMode(self):
        result = self.sshClient.execute("config t")[0]
        if not self.__isValidResponse(result):
            print "Failed to enter config mode"
            return False
        self.inConfigMode = True
        return True

    def enterInterfaceConfig(self, interface):
        result = self.sshClient.execute("int {0}".format(interface))[0]
        if not self.__isValidResponse(result):
            print "Failed to enter config mode on interface {0}".format(interface)
            return False
        self.inInterface = True
        return False

    def leaveConfigMode(self):
        result = self.sshClient.execute("end")[0]
        if not self.__isValidResponse(result):
            print "Failed to exit config mode"
            return False
        self.inConfigMode = False
        return True

    def leaveInterfaceConfig(self):
        result = self.sshClient.execute("exit")[0]
        if not self.__isValidResponse(result):
            print "Failed to exit config mode"
            return False
        self.inInterface = False
        return True

    def write(self):
        result = self.sshClient.execute("write")[0]
        if "OK" in result:
            return True
        else:
            print "Failed to write configuration, result: {0}".format(result)
            return False

    def setSpeed(self, newSpeed, no=False):
        if not self.inConfigMode:
            print "can't set speed when not in config mode"
            return False
        if not self.inInterface:
            print "can't set speed when not configuring interface"
            return False
        result = None
        if no:
            result = self.sshClient.execute("no {0}".format(Speed.switchCommand(newSpeed)))[0]
        else:
            result = self.sshClient.execute("{0}".format(Speed.switchCommand(newSpeed)))[0]
        if not self.__isValidResponse(result):
            print "Failed to set speed, speed {0} may be bad".format(newSpeed)
            return False
        return True

    def setDescription(self, newDescription, no=False):
        if not self.inConfigMode:
            print "can't set description when not in config mode"
            return False
        if not self.inInterface:
            print "can't set description when not configuring interface"
            return False
        result = None
        if no:
            result = self.sshClient.execute("no description {0}".format(newDescription))[0]
        else:
            result = self.sshClient.execute("description {0}".format(newDescription))[0]
        if not self.__isValidResponse(result):
            print "Failed to set speed, description {0} may be bad".format(newDescription)
            return False
        return True

    def setDuplex(self, newSpeed, no=False):
        if not self.inConfigMode:
            print "can't set duplex when not in config mode"
            return False
        if not self.inInterface:
            print "can't set duplex when not configuring interface"
            return False
        duplex = ""
        if newSpeed.duplex == Speed.DUPLEX_FULL:
            duplex = "full"
        elif newSpeed.duplex == Speed.DUPLEX_HALF:
            duplex = "half"
        else:
            duplex = "auto"
        result = None
        if no:
            result = self.sshClient.execute("no duplex {0}".format(duplex))[0]
        else:
            result = self.sshClient.execute("duplex {0}".format(duplex))[0]
        if not self.__isValidResponse(result):
            print "Failed to set speed, duplex {0} may be bad".format(duplex)
            return False
        return True

    def shutdown(self, no=False):
        if not self.inConfigMode:
            print "can't set speed when not in config mode"
            return False
        if not self.inInterface:
            print "can't set speed when not configuring interface"
            return False
        result = None
        if no:
            result = self.sshClient.execute("no shutdown")[0]
        else:
            result = self.sshClient.execute("shutdown")[0]
        if not self.__isValidResponse(result):
            print "Failed to set shutdown status on port"
            return False
        return True

    def setSwitchportMode(self, mode):
        if not self.inConfigMode:
            print "can't set speed when not in config mode"
            return False
        if not self.inInterface:
            print "can't set speed when not configuring interface"
            return False
        result = None
        if mode == "access":
            result = self.sshClient.execute("switchport mode access")[0]
        elif mode == "trunk":
            result = self.sshClient.execute("switchport mode trunk")[0]
        else:
            print "Invalid switchport mode, {0} not supported".format(mode)
            return False
        if not self.__isValidResponse(result):
            print "Failed to set switchport mode"
            return False
        return True
