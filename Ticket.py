from PIC import PIC


class Ticket:
    number = None               # the ticket number this ticket represents (not used)
    dueby = None                # the dueby date for a ticket (not used)
    priority = None             # the priority of the ticket (not used)
    status = None               # the status of the ticket (not used)
    pics = None                 # list of all PICs in this ticket, provider supplied or not
    configurablePics = None     # list of PICs with a provider port that can be configured
    picNames = None             # [name] -> PIC object

    def __init__(self, number, dueby, priority, status):
        self.number = number
        self.dueby = dueby
        self.priority = priority
        self.status = status
        self.pics = []
        self.configurablePics = []
        self.picNames = dict()

    def __containsPic(self, pic):
        return self.picNames.has_key(pic)

    @staticmethod
    # x < y: -1, x == y: 0, x > y: 1
    def __cmp(x, y):
        xProvider = None
        yProvider = None
        try:
            xProvider = x.getProvider()
        except AttributeError:
            xProvider = None
        try:
            yProvider = y.getProvider()
        except AttributeError:
            yProvider = None
        # Handle null
        if xProvider is None and yProvider is not None:
            return -1
        elif xProvider is not None and yProvider is None:
            return 1
        elif xProvider is None and yProvider is None:
            return 0
        return (yProvider.TR < xProvider.TR) - (yProvider.TR > xProvider.TR)

    def __sort(self):
        # cmp=lambda x, y: (y.newProvider.TR < x.newProvider.TR) - (y.newProvider.TR > x.newProvider.TR)
        self.pics = sorted(self.pics, cmp=Ticket.__cmp)

    def addPic(self, pic):
        if not isinstance(pic, PIC):
            raise AttributeError("Can't add a pic that isn't of type PIC")
        if not self.__containsPic(pic):
            self.pics.append(pic)
            self.picNames[pic.name] = pic
            try:
                if pic.getProvider() is not None:
                    self.configurablePics.append(pic)
            except AttributeError:
                pass            # do nothing
            self.__sort()
        else:
            raise ValueError("PIC already added")

