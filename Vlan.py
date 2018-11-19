class Vlan:
    ipAddress = None        # 128.046.083.000
    tag = None              # 383
    name = ""               # Public Subnet
    mask = None             # 24
    trunk = False           # whether the vlan is trunk or not
    voice = False           # whether the vlan is a voice vlan

    def __init__(self, risqueString=None, switchString=None):
        if risqueString is not None:
            self.__resolveVlanFromRisque(risqueString)
        if switchString is not None:
            self.__resolveVlanFromSwitch(switchString)

    # Fills out the vlan object from the risque string
    # 128.046.083.000/24 Public Subnet (383) resolves to ip: 128.046.083.000, tag: 383, name: Public Subnet, mask: 24
    # 172.021.008.0/24-SSTA Host Printers Only (695) resolves to ip: 172.021.008.0, tag: 695, name: SSTA Host Printers Only, mask: 24
    # risque is case-sensitive
    def __resolveVlanFromRisque(self, risque):
        if risque is None:
            raise AttributeError("risqueString attribute is None")
        if type(risque) is not str:
            raise TypeError("risqueString attribute is not a string")
        # ['128.046.083.000', '24 Public Subnet (383)']
        ipSplit = risque.split('/')
        if len(ipSplit) is 1:
            raise AttributeError("risqueString is not a valid vlan")
        self.ipAddress = ipSplit[0]
        # ['24', 'Public', 'Subnet', '(383)']
        spaceSplit = ipSplit[1].split(' ')
        try:
            self.mask = int(spaceSplit[0])
        except ValueError:
            # Fails for '24-SSTA'
            # ['24', 'SSTA']
            maskSplit = spaceSplit[0].split('-')
            self.mask = int(maskSplit[0])
            # Fix for case: 010.162.017.000/24-STEW-CSDS-Supported_Computers_1 (1211)
            for i in range(1, len(maskSplit)):
                self.name += maskSplit[i]
                if i is not len(maskSplit) - 1:
                    self.name += '-'

        for i in range(1, len(spaceSplit) - 1):
            self.name += spaceSplit[i]
            if i is not len(spaceSplit) - 2:
                self.name += ' '
        # '(383)'
        tagRaw = spaceSplit[len(spaceSplit) - 1]
        if '(' not in tagRaw or ')' not in tagRaw:
            self.tag = None
            # Fix for case: 128.210.071.000/24 Public Subnet
            # Case requires manually adding the tag later
            self.name += ' '
            self.name += spaceSplit[len(spaceSplit) - 1]
        else:
            self.tag = int(tagRaw.strip('(').strip(')'))

    # Fills out the vlan object from the switch string
    # switchport access vlan 368 resolves to tag: 368
    # switchport voice vlan 3036 resolves to tag: 3036, voice: True
    # switchport trunk native vlan 1000 resolves to tag: 1000, trunk: True
    # switchport trunk allowed vlan 368,775,776,857,1000,1001,1319-1321,3036 fails resolve, use Vlan.AllowedVlanList() instead
    def __resolveVlanFromSwitch(self, switch):
        if switch is None:
            raise AttributeError('switchString attribute is None')
        if type(switch) is not str:
            raise ValueError('switchString attribute is not a string')
        if "trunk allowed vlan" in switch:
            raise AttributeError('switchString attribute contains a vlan list')
        # ['switchport', 'access', 'vlan', '368']
        vlanSplit = switch.split(' ')
        # 368
        self.tag = int(vlanSplit[len(vlanSplit) - 1])
        if "voice" in switch:
            self.voice = True
        elif "trunk" in switch:
            self.trunk = True
        self.name = None

    def setTag(self, tag):
        self.tag = tag

    # Creates a list of allowed vlans on a trunk port
    # switchport trunk allowed vlan 368,775,776,857,1000,1001,1319-1321,3036 resolves to [368,775,776,857,1000,1001,1319,1320,1321,3036]
    # switchport trunk allowed vlan add 2700,3017 resolves to [2700,3017]
    # if an 'allowed vlan add' is called, join the two lists with JoinAllowedVlanList
    @staticmethod
    def AllowedVlanList(switch):
        if switch is None:
            raise AttributeError("switchString attribute is None")
        if type(switch) is None:
            raise ValueError("switchString attribute is not a string")
        if "trunk allowed vlan" not in switch:
            raise AttributeError("switchString does not contain a vlan list")
        list = []
        # ['switchport', 'trunk', 'allowed', 'vlan', '368,775,776,857,1000,1001,1319-1321,3036']
        vlanSplit = switch.split(' ')
        # '368,775,776,857,1000,1001,1319-1321,3036'
        allowedVlans = vlanSplit[len(vlanSplit) - 1]
        # ['368', '775', '776', '857', '1000', '1001', '1319-1321', '3036']
        vlans = allowedVlans.split(',')
        for vlan in vlans:
            # case '1319-1321'
            if '-' in vlan:
                # ['1319', '1321']
                rangeSplit = vlan.split('-')
                lowerRange = int(rangeSplit[0])
                upperRange = int(rangeSplit[1])
                for i in range(lowerRange, upperRange + 1):
                    newVlan = Vlan()
                    newVlan.setTag(i)
                    if not Vlan.tagInVlanList(list, newVlan.tag):
                        list.append(newVlan)
            else:
                newVlan = Vlan()
                newVlan.setTag(int(vlan))
                if not Vlan.tagInVlanList(list, newVlan.tag):
                    list.append(newVlan)
        return list

    # Joins two list of allowed vlans to one list of allowed vlans
    # list1: [368,776,3036], list2: [2700,3017] resolves to [368,776,2700,3017,3036]
    @staticmethod
    def JoinAllowedVlanList(list1, list2):
        if list1 is None or list2 is None:
            raise AttributeError("one or more list attributes is None")
        if type(list1) is not list or type(list2) is not list:
            raise ValueError("one or more list attributes is not a list")
        combinedList = []
        for item in list1:
            if not Vlan.tagInVlanList(combinedList, item.tag):
                combinedList.append(item)
        for item in list2:
            if not Vlan.tagInVlanList(combinedList, item.tag):
                combinedList.append(item)
        # StackOverflow: https://stackoverflow.com/a/8479025
        # (y.tag > x.tag) - (y.tag < x.tag)
        combinedList.sort(cmp=lambda x, y: (y.tag < x.tag) - (y.tag > x.tag))
        return combinedList
    def printDebug(self):
        print "ip: {0}, tag: {1}, name: {2}, mask: {3}, trunk? {4}, voice? {5}"\
            .format(self.ipAddress, self.tag, self.name, self.mask, self.trunk, self.voice)

    # Returns true if a tag already exists in a vlan list, false if it doesn't
    @staticmethod
    def tagInVlanList(list, tag):
        if list is None or tag is None:
            return False
        for vlanObj in list:
            if not isinstance(vlanObj, Vlan):
                return False
            if vlanObj.tag == tag:
                return True
        return False

