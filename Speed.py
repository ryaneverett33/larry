class Speed:
    DUPLEX_AUTO = "auto"
    DUPLEX_FULL = "full"
    DUPLEX_HALF = "half"
    NAME_TEN = "10"
    NAME_FAST = "Fast"
    NAME_GIGABIT = "Gigabit"
    NAME_TENGIGABIT = "10Gigabit"

    name = None         # 10, Fast, Gigabit, 10Gigabit,
    duplex = None       # auto, full, half
    speedTuple = None   # 10, 100, 1000, 2500, 5000, 10000
    speedAuto = False

    def __init__(self, name=None, risqueString=None, switchString=None):
        if name is not None:
            self.__resolveSpeedFromName(name)
        elif risqueString is not None:
            self.__resolveSpeedFromRisque(risqueString)
        elif switchString is not None:
            self.__resolveSpeedFromSwitch(switchString)

    # Fills out the Speed object from a default speed type, duplex auto
    # FastEthernet (name='fast') resolves to 10/100, Gigabit (name='gigabit') resolves to 10/100/1000
    # name is case-insensitive
    def __resolveSpeedFromName(self, name):
        if name is None:
            raise AttributeError("name attribute is None")
        if type(name) is not str:
            raise TypeError("name attribute is not a string")
        if name == "10":
            self.duplex = self.DUPLEX_AUTO
            self.__fillTuple(ten=1)
            self.name = self.NAME_TEN
        elif name.lower() == "fast":
            self.duplex = self.DUPLEX_AUTO
            self.__fillTuple(ten=1, hundred=1)
            self.name = self.NAME_FAST
        elif name.lower() == "gigabit":
            self.duplex = self.DUPLEX_AUTO
            self.__fillTuple(ten=1, hundred=1, gig=1)
            self.name = self.NAME_GIGABIT
        elif name.lower() == "10gigabit":
            self.duplex = self.DUPLEX_AUTO
            self.__fillTuple(ten=1, hundred=1, gig=1, twogig=1, fivegig=1, tengig=1)
            self.name = self.NAME_TENGIGABIT
        else:
            raise AttributeError("name is an invalid type")

    # Fills out the Speed object from a default risque speed type
    # 1000T-SW-F resolves to 1000, duplex full, 100/1000T-SW-A resolves to 100/1000, duplex auto
    # risque is case-sensitive
    def __resolveSpeedFromRisque(self, risque):
        if risque is None:
            raise AttributeError("risqueString attribute is None")
        if type(risque) is not str:
            raise TypeError("risqueString attribute is not a string")
        # fill out speed first
        if "10T" in risque:
            self.__fillTuple(ten=1)
        elif "100T" in risque:
            self.__fillTuple(hundred=1)
        elif "1000T" in risque:
            self.__fillTuple(gig=1)
        elif "10/100T" in risque:
            self.__fillTuple(ten=1, hundred=1)
        elif "10/100/100T" in risque:
            self.__fillTuple(ten=1, hundred=1, gig=1)
        elif "100/1000T" in risque:
            self.__fillTuple(hundred=1, gig=1)
        elif "100/1000/2.5G/5G/10G" in risque:
            self.__fillTuple(hundred=1, gig=1, twogig=1, fivegig=1, tengig=1)
        else:
            raise AttributeError("Risque String is not supported! Error: Speed")
        # fill out duplex
        if "SW-A" in risque:
            self.duplex = self.DUPLEX_AUTO
        elif "SW-H" in risque:
            self.duplex = self.DUPLEX_HALF
        elif "SW-F" in risque:
            self.duplex = self.DUPLEX_FULL
        else:
            raise AttributeError("Risque String is not supported! Error: Duplex")

    # Fills out the speed object from a default switch speed type, duplex auto
    # speed auto 10 100 100 resolves to 10/100/1000
    # speed is case-insensitive
    def __resolveSpeedFromSwitch(self, switch):
        if switch is None:
            raise AttributeError("switchString attribute is None")
        if type(switch) is not str:
            raise TypeError("switchString attribute is not a string")
        ten = None
        hundred = None
        gig = None
        twogig = None
        fivegig = None
        tengig = None
        if "10" in switch:
            ten = True
        if "100" in switch:
            hundred = True
        if "1000" in switch:
            gig = True
        if "2.5G" in switch.upper() or "2500" in switch:
            twogig = True
        if "5G" in switch.upper() or "5000" in switch:
            fivegig = True
        if "10G" in switch.upper() or "10000" in switch:
            tengig = True
        self.__fillTuple(ten, hundred, gig, twogig, fivegig, tengig)
        if "auto" in switch.lower():
            self.speedAuto = True

    # Sets the duplex of the speed object
    # Necessary for reading from switch configs
    # duplex is case-insensitive
    def setDuplex(self, duplex):
        if duplex is None:
            raise AttributeError("duplex attribute is None")
        if type(duplex) is not str:
            raise TypeError("duplex attribute is not a string")
        if "auto" is duplex.lower():
            self.duplex = self.DUPLEX_AUTO
        elif "half" is duplex.lower():
            self.duplex = self.DUPLEX_HALF
        elif "full" is duplex.lower():
            self.duplex = self.DUPLEX_FULL
        else:
            raise AttributeError("Duplex is not supported!")

    # returns a speed object with an empty speed tuple set to speed auto and duplex auto
    @staticmethod
    def SpeedAutoObject():
        speed = Speed()
        speed.setDuplex(speed.DUPLEX_AUTO)
        speed.__fillTuple()
        speed.speedAuto = True
        return speed

    # Fills the speed Tuple
    def __fillTuple(self, ten=None, hundred=None, gig=None, twogig=None, fivegig=None, tengig=None):
        self.speedTuple = [0,0,0,0,0,0]
        if ten is not None or ten:
            self.speedTuple[0] = 10
        if hundred is not None or hundred:
            self.speedTuple[1] = 100
        if gig is not None or gig:
            self.speedTuple[2] = 1000
        if twogig is not None or twogig:
            self.speedTuple[3] = 2500
        if fivegig is not None or fivegig:
            self.speedTuple[4] = 5000
        if tengig is not None or tengig:
            self.speedTuple[5] = 10000

    def printDebug(self):
        print "name: {0}, duplex: {1}, auto? {2}, tuple: {3}".format(self.name, self.duplex, self.speedAuto, self.speedTuple)