from PIC import PIC

class Ticket:
    number = None
    dueby = None
    priority = None
    status = None
    pics = None
    picNames = None     # [name] -> PIC object

    def __init__(self, number, dueby, priority, status):
        self.number = number
        self.dueby = dueby
        self.priority = priority
        self.status = status
        self.pics = []
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
            self.__sort()
        else:
            raise ValueError("PIC already added")

