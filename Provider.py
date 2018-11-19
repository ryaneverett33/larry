class Provider:
    building = None     # e.g. YONG
    TR = None           # e.g. 286
    stack = None        # e.g. 1
    switch = None       # e.g. 3
    port = None         # e.g 18
    switchType = None   # e.g. c3750ep
    intType = None      # Gi, Te, Tw, Fa
    uplink = False      # e.g. Te1/1/3
    def __init__(self, risqueString=None, switchString=None):
        if risqueString is not None:
            self.__parseProviderFromRisque(risqueString)
        if switchString is not None:
            self.__parseProviderFromSwitch(switchString)

    # Fills out the provider object from a risque type
    # hamp-gu01a-c3750ep-01:04-Gi4/0/18 resolves to building: hamp, TR: gu01a, stack: 1, switch: 4
    def __parseProviderFromRisque(self, risque):
        if risque is None:
            raise AttributeError("risqueString attribute is None")
        if type(risque) is not str:
            raise ValueError("risqueString attribute is not a string")
        # ['hamp-gu01a-c3750ep-01', '04-Gi4/0/18']
        risqueSplit = risque.split(':')
        if len(risqueSplit) != 2:
            raise AttributeError("risqueString is not a valid provider!")
        # ['hamp', 'gu01a', 'c3750ep', '01']
        buildingSplit = risqueSplit[0].split('-')
        self.building = buildingSplit[0].lower()
        self.TR = buildingSplit[1].lower()
        self.stack = int(buildingSplit[3])
        self.switchType = buildingSplit[2]
        # ['04', 'Gi4/0/18']
        switchSplit = risqueSplit[1].split('-')
        self.switch = int(switchSplit[0])
        # ['Gi4', '0', '18']
        providerSplit = switchSplit[1].split('/')
        self.port = int(providerSplit[len(providerSplit) - 1])
        self.intType = providerSplit[0][0:len(providerSplit[0]) - 1]

    # Fills out the provider object from the switch type
    # GigabitEthernet1/0/9 resolves to switch 1, port 9, intType: Gi
    # Gi3/0/12 resolves to switch 3, port 12, intType: Gi
    # Te1/1/3 resolves to switch 1, port 3, intType Te, uplink = True
    # Te2/3/16 doesn't resolve as it refers to a chassis
    # FastEthernet0/1 resolves to switch 0, port 1, intType Fa
    def __parseProviderFromSwitch(self, switch):
        if switch is None:
            raise AttributeError("switchString attribute is None")
        if type(switch) is not str:
            raise ValueError("switchString attribute is not a string")
        # ['GigabitEthernet1', '0', '9'], ['Fa0', '8']
        providerSplit = switch.split('/')
        if len(providerSplit) < 2:
            raise AttributeError("switchString is an invalid provider")
        # ['Gi3', '0']
        rawType = providerSplit[0][0:len(providerSplit[0])-1]
        self.switch = int(providerSplit[0][len(providerSplit[0]) - 1])
        if len(rawType) > 2:
            if "GigabitEthernet" == rawType:
                self.intType = "Gi"
            elif "TwoGigabitEthernet" == rawType:
                self.intType = "Tw"
            elif "TenGigabitEthernet" == rawType:
                self.intType = "Te"
            elif "FastEthernet" == rawType:
                self.intType = 'Fa'
            else:
                raise AttributeError("switchSting is not a valid provider!")
        else:
            self.intType = rawType
        # ['Fa0', '8']
        if len(providerSplit) == 2:
            self.port = int(providerSplit[1])
        else:
            self.port = int(providerSplit[2])
            if providerSplit[1] != '0':
                if providerSplit[1] != '1':
                    raise AttributeError("switchString is a line card, not supported!")
                self.uplink = True

