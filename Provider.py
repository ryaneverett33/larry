class Provider:
    building = None     # e.g. YONG
    TR = None           # e.g. 286
    stack = None        # e.g. 1
    switch = None       # e.g. 3
    port = None         # e.g 18
    switchType = None   # e.g. c3750ep
    intType = None      # e.g. Gi, Te, Tw
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
        self.intType = providerSplit[0][0:len(providerSplit[0] - 1)]

    def __parseProviderFromSwitch(self, switch):
        if switch is None:
            raise AttributeError("switchString attribute is None")
        if type(switch) is not str:
            raise ValueError("switchString attribute is not a string")