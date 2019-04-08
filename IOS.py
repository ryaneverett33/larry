from Vlan import Vlan
from Speed import Speed
from procedures import BaseTemplates
from Provider import Provider
import re


# Represents an SSH connection to an IOS switch
class IOS:
    sshClient = None
    host = None
    switchType = None   # e.g. c3750ep
    inConfigMode = False
    inInterface = False
    isFexHost = False
    macAddrRegEx = re.compile("[0-9a-zA-Z]{4}.[0-9a-zA-Z]{4}.[0-9a-zA-Z]{4}")
    vlanRegEx = re.compile("[0-9]+")
    voiceVlan = None
    POWER_NO = "never"
    POWER_AUTO = "auto"
    apcTrippliteDeviceRegex = "(apc)[A-z0-9]+|(trp)[A-z0-9]+"

    def __init__(self, sshClient, host, switchType):
        voiceVlan = None
        self.sshClient = sshClient
        if self.sshClient.connected:
            self.sshClient.disconnect()
        self.sshClient.connect(host)
        self.switchType = switchType
        if self.sshClient.isForbiddenHost():
            self.disconnect()
            raise NotImplementedError("Not allowed to make changes on host {0}, Reason: DISALLOWED_HOST".format(host))
        if self.sshClient.isFexHost():
            self.isFexHost = True

    # Return [Port, Name, Status, Vlan, Duplex, Speed, Type]
    def __sisSplit(self, line):
        splat = line.split(' ')
        arr = []
        for i in range(0, len(splat)):
            word = splat[i]
            if len(word) < 1:
                continue
            if "Not" in word and "Present" in splat[i + 1]:
                arr.append("Not Present")
                continue
            arr.append(word)
        return arr

    # Return array of Tuples[Port, Name, Status, Vlan, Duplex, Speed, Type]
    def __sis(self, include=None):
        # [output, hostname]
        result = None
        if include is not None:
            if self.inConfigMode:
                print "IOS::getConfig() in Config Mode!!"
                result = self.sshClient.execute('do show int status | {0}'.format(include))
            else:
                result = self.sshClient.execute('show int status | i {0}'.format(include))
        else:
            if self.inConfigMode:
                print "IOS::getConfig() in Config Mode!!"
                result = self.sshClient.execute('do show int status')
            else:
                result = self.sshClient.execute('show int status')
        rawLines = result[0].split('\n')
        lines = []
        for line in rawLines:
            if "Port" in line and "Name" in line:
                # skip header
                continue
            if len(line) <= 1:
                continue
            lines.append(self.__sisSplit(line))

        return lines

    def __macAddressTableSplit(self, line):
        splat = line.split(' ')
        arr = []
        for i in range(0, len(splat)):
            word = splat[i]
            if len(word) < 1:
                continue
            arr.append(word)
        return arr

    # Dirty hack to get sis working for large switches
    def sis(self, include=None):
        result = self.__sis(include)
        if include is None:
            return self.__sis()
        return result

    def findInterfaceOfPic(self, picName):
        sis = self.sis(include=picName.lower())
        for arr in sis:
            interface = arr[0]
            name = arr[1]
            if name.lower() == picName.lower():
                return interface
        return None

    def findFexInterface(self, pic, provider):
        # search sis if the pic name already exists
        sisBasicSearch = self.findInterfaceOfPic(pic.name)
        if sisBasicSearch is not None:
            return sisBasicSearch
        # PicName hasn't been added to sis (e.g. Activate)
        # Find virtual switch (e.g. Gi112 or Gi132)
        interfaces = self.sis(include=provider.building.lower())
        if len(interfaces) == 0:
            return None
        else:
            for interface in interfaces:
                port = interface[0]
                name = interface[1]
                if ("Te" in port or "Po" in port) or (provider.building.lower() in name and provider.TR.lower() in name):
                    continue
                if "Gi" in port:
                    neighborProvider = Provider(switchString=port)
                    # Gi103/1/0/9
                    return "{0}{1}/1/0/{2}".format(neighborProvider.intType, neighborProvider.switch, provider.port)
            return None

    def disconnect(self):
        self.sshClient.disconnect()

    def __isValidResponse(self, commandResponse):
        passed = True
        passed = (True, False)[not passed or "Invalid input" in commandResponse]
        passed = (True, False)[not passed or "not supported" in commandResponse]
        return passed

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

    def getDuplex(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "duplex" in line:
                return Speed.resolveDuplexFromSwitch(line)
        return None

    # gets the current number of UPSs in the TR
    def getUPSCount(self):
        # sis | i (apc)[A-z0-9]+|(trp)[A-z0-9]+ returns all apc/tripplite devices
        devices = self.sis(include=self.apcTrippliteDeviceRegex)
        deviceCount = 0
        if devices is None or len(devices) == 0:
            return deviceCount
        upsList = Hosts.getUPSList()
        for device in devices:
            if device in upsList:
                deviceCount = deviceCount + 1
        return deviceCount

    def getPower(self, interface, config=None):
        useConfig = config
        if useConfig is None:
            useConfig = self.getConfig(interface, flatten=False)
        for line in useConfig:
            if "power" in line:
                if "no" in line:
                    return self.POWER_NO
                elif "auto" in line:
                    return self.POWER_AUTO
                elif "never" in line:
                    return self.POWER_NO
                elif "max" in line:
                    # get max power level
                    # [' power inline port ', ' 20000']
                    lineSplit = line.split("maximum")
                    if len(lineSplit) != 2:
                        return None
                    return int(lineSplit[1])

        return self.POWER_AUTO  # if the switch has no power setting, the default is auto

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
        vlan = None
        for line in useConfig:
            if "switchport trunk allowed" in line:
                vlan2 = Vlan.AllowedVlanList(line)
                if vlan is None:
                    vlan = vlan2
                else:
                    vlan = Vlan.JoinAllowedVlanList(vlan, vlan2)
        return vlan

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
            tag = None
            if isinstance(newVlan, Vlan):
                tag = newVlan.tag
            elif isinstance(newVlan, str):
                tag = newVlan
            result = self.sshClient.execute("no switchport access vlan {0}".format(tag))[0]
        else:
            tag = None
            if isinstance(newVlan, Vlan):
                tag = newVlan.tag
            elif isinstance(newVlan, str):
                tag = newVlan
            result = self.sshClient.execute("switchport access vlan {0}".format(tag))[0]
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
            tag = None
            if isinstance(newVoiceVlan, Vlan):
                tag = newVoiceVlan.tag
            elif isinstance(newVoiceVlan, str):
                tag = newVoiceVlan
            result = self.sshClient.execute("no switchport voice vlan {0}".format(tag))[0]
        else:
            tag = None
            if isinstance(newVoiceVlan, Vlan):
                tag = newVoiceVlan.tag
            elif isinstance(newVoiceVlan, str):
                tag = newVoiceVlan
            result = self.sshClient.execute("switchport voice vlan {0}".format(tag))[0]
        if not self.__isValidResponse(result):
            print "Failed to set voice vlan, vlan {0} may be bad".format(newVoiceVlan)
            return False
        return True

    def setNativeVlan(self, newNativeVlan):
        if not self.inConfigMode:
            print "can't set voice vlan when not in config mode"
            return False
        if not self.inInterface:
            print "can't set voice vlan when not configuring interface"
            return False
        tag = None
        if isinstance(newNativeVlan, Vlan):
            tag = newNativeVlan.tag
        elif isinstance(newNativeVlan, str):
            tag = newNativeVlan
        result = self.sshClient.execute("switchport trunk native vlan {0}".format(tag))[0]
        if not self.__isValidResponse(result):
            print "Failed to set native vlan, vlan {0} may be bad".format(newNativeVlan)
            return False
        return True

    # sets switchport trunk allowed vlan 3,4 so that vlans can be added
    def setTaggedVlans(self, newTaggedVlans):
        if not self.inConfigMode:
            print "can't set voice vlan when not in config mode"
            return False
        if not self.inInterface:
            print "can't set voice vlan when not configuring interface"
            return False
        string = "switchport trunk allowed vlan "
        if isinstance(newTaggedVlans, list):
            for i in range(0, len(newTaggedVlans)):
                string = string + str(newTaggedVlans[i].tag)
                if i != len(newTaggedVlans) - 1:
                    string = string + ','
        elif isinstance(newTaggedVlans, Vlan):
            string = string + str(newTaggedVlans.tag)
        result = self.sshClient.execute(string)
        if not self.__isValidResponse(result):
            print "Failed to set tagged vlans"
            return False
        return True

    def addTaggedVlans(self, newTaggedVlans):
        if not self.inConfigMode:
            print "can't set voice vlan when not in config mode"
            return False
        if not self.inInterface:
            print "can't set voice vlan when not configuring interface"
            return False
        string = "switchport trunk allowed vlan add "
        if isinstance(newTaggedVlans, list):
            for i in range(0, len(newTaggedVlans)):
                string = string + str(newTaggedVlans[i].tag)
                if i != len(newTaggedVlans) - 1:
                    string = string + ','
        elif isinstance(newTaggedVlans, Vlan):
            string = string + str(newTaggedVlans.tag)
        result = self.sshClient.execute(string)
        if not self.__isValidResponse(result):
            print "Failed to set tagged vlans"
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

    def getBaseTemplate(self):
        if "3750" in self.switchType:
            return BaseTemplates.BaseTemplates.template3750
        elif "3850" in self.switchType:
            return BaseTemplates.BaseTemplates.template3850
        elif "9348" in self.switchType or "9300" in self.switchType:
            return BaseTemplates.BaseTemplates.template9300
        elif "3560" in self.switchType:
            return BaseTemplates.BaseTemplates.template3560
        elif "2960" in self.switchType:
            return BaseTemplates.BaseTemplates.template2960
        else:
            return None

    def applyBaseTemplate(self, template):
        if not self.inConfigMode:
            print "can't apply base config when not in config mode"
            return False
        if not self.inInterface:
            print "can't apply base config when not configuring interface"
            return False
        result = self.sshClient.execute(template)[0]
        if not self.__isValidResponse(result):
            print "Failed to set config from base template"
            return False
        return True

    def isInterfaceEmpty(self, switchConfig, flatten=False):
        useConfig = switchConfig
        if not flatten:
            useConfig = self.__flatten(switchConfig)
        if "3560" in self.switchType:
            return BaseTemplates.BaseTemplates.isInterfaceEmpty(useConfig, "3560")
        elif "3750" in self.switchType:
            return BaseTemplates.BaseTemplates.isInterfaceEmpty(useConfig, "3750")
        elif "2960" in self.switchType:
            return BaseTemplates.BaseTemplates.isInterfaceEmpty(useConfig, "2960")
        elif "3850" in self.switchType:
            return BaseTemplates.BaseTemplates.isInterfaceEmpty(useConfig, "3850")
        elif "9300" in self.switchType or "9348" in self.switchType:
            return BaseTemplates.BaseTemplates.isInterfaceEmpty(useConfig, "9300")
        else:
            raise AttributeError("Unknown switch type, unable to determine whether it's empty")

    def getConnectionState(self, interface):
        connection = None
        if self.inConfigMode:
            print "IOS::getConfig() in Config Mode!!"
            connection = self.sshClient.execute("do show int {0}".format(interface))[0]
        else:
            connection = self.sshClient.execute("show int {0}".format(interface))[0]
        if "connected" in connection:
            return "connected"
        elif "notconnect" in connection:
            return "notconnect"
        elif "disabled" in connection:
            return "disabled"
        elif "err-disabled" in connection:
            return "err-disabled"
        else:
            raise ValueError("Interface is in unrecognized state")

    # return array of (vlan, mac-address)
    def getMacAddresses(self, interface):
        addressTable = None
        if self.inConfigMode:
            print "IOS::getConfig() in Config Mode!!"
            addressTable = self.sshClient.execute("do mac address-table int {0}".format(interface))[0]
        else:
            addressTable = self.sshClient.execute("mac address-table int {0}".format(interface))[0]
        rows = addressTable.split('\n')
        addresses = list()
        for i in range(0, len(rows)):
            if i < 4:
                continue
            # '1000    001d.b340.9ac0    DYNAMIC     Po1'
            rowSplit = self.__macAddressTableSplit(rows[i])
            tup = [None, None]
            for column in rowSplit:
                if tup[0] is None and self.vlanRegEx.match(column) is not None:
                    tup[0] = column
                elif tup[1] is None and self.macAddrRegEx.match(column) is not None:
                    tup[1] = column
                if tup[0] is not None and tup[1] is not None:
                    break
            if tup[0] is not None:
                addresses.append(tup)
        return addresses

    def findVoiceVlan(self):
        if self.voiceVlan is not None:
            return self.voiceVlan
        else:
            result = self.sshClient.execute('show running-config | i switchport voice vlan')[0]
            lines = result.split('\n')
            if len(lines) == 0:
                return None
            else:
                for line in lines:
                    if "switchport voice vlan" in line:
                        # switchport voice vlan 3022
                        words = line.split(' ')
                        for word in words:
                            if self.vlanRegEx.match(word) is not None:
                                self.voiceVlan = word.strip()
                                return self.voiceVlan
                return None

    # Executes an arbitrary command, basically like ssh.execute() but with basic command verifcation
    def do(self, switchCommand):
        result = self.sshClient.execute(switchCommand)[0]
        if not self.__isValidResponse(result):
            print "{0} failed to execute".format(switchCommand)
        return result
