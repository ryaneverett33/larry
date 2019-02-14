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

    def __sort(self):
        self.pics = sorted(self.pics, cmp=lambda x, y: (y.newProvider.TR < x.newProvider.TR) - (y.newProvider.TR > x.newProvider.TR))

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

